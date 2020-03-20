from bin.service import Environment
from bin.service import Map
from shutil import copyfile
import pickle
import os
import time
import datetime
import numpy


class Cache:
    """Cache handler"""

    def __init__(self):
        self.environment = Environment.Environment()
        self.mapper = Map.Map()

    def load_token(self):
        token_file = self.environment.get_path_token()
        file_exists = os.path.isfile(token_file)
        if file_exists:
            file = open(token_file, "rb")
            token = pickle.load(file)
        else:
            token = None
        return token

    def store_token(self, token):
        token_file = self.environment.get_path_token()
        file = open(token_file, "wb")
        pickle.dump(token, file)

    def store_ticket(self, jira_id, ticket):
        is_valid = self.validate_ticket_data(ticket)
        if is_valid:
            cache_file = self.environment.get_path_cache()
            content = self.load_cached_tickets()
            content[str(jira_id)] = ticket
            file = open(cache_file, "wb")
            pickle.dump(content, file)
        return is_valid

    def load_jira_id_for_key(self, jira_key):
        jira_key_path = self.environment.get_path_jira_key()
        file_exists = os.path.exists(jira_key_path)
        if file_exists:
            file = open(jira_key_path, "rb")
            content = pickle.load(file)
            if jira_key in content:
                return str(content[jira_key])

        return None

    def load_jira_key_for_id(self, jira_id):
        jira_key_path = self.environment.get_path_jira_key()
        file_exists = os.path.exists(jira_key_path)
        if file_exists:
            file = open(jira_key_path, "rb")
            content = pickle.load(file)
            for key, content_id in content.items():
                if content_id == jira_id:
                    return key

        return None

    def store_jira_key_and_id(self, jira_key, jira_id):
        jira_key_path = self.environment.get_path_jira_key()
        file_exists = os.path.exists(jira_key_path)
        if file_exists:
            file = open(jira_key_path, "rb")
            content = pickle.load(file)
        else:
            content = {}
        content[str(jira_key)] = str(jira_id)
        file = open(jira_key_path, "wb")
        pickle.dump(content, file)

    @staticmethod
    def validate_ticket_data(ticket_data):
        for i in ticket_data:
            is_valid = ticket_data[i] is not None
            if is_valid:
                return True
        return False

    def load_cached_tickets(self):
        cache_file = self.environment.get_path_cache()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        return content

    def load_jira_keys_and_ids(self):
        cache_file = self.environment.get_path_jira_key()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        return content

    def add_lost_jira_key(self, jira_key):
        cache_file = self.environment.get_path_lost_jira_key()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {'jira_keys': []}
        if jira_key not in content['jira_keys']:
            content['jira_keys'].append(jira_key)
        file = open(cache_file, "wb")
        pickle.dump(content, file)

    def remove_jira_key(self, jira_key):
        cache_file = self.environment.get_path_jira_key()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        if jira_key in content:
            del(content[jira_key])
        file = open(cache_file, "wb")
        pickle.dump(content, file)

    def update_all_tickets(self, sd_api):
        success = True
        failed_jira_keys = []
        clean_cache = {}
        jira_keys_and_ids = self.load_jira_keys_and_ids()
        current_ticket = 0
        for jira_key in jira_keys_and_ids:
            current_ticket += 1
            jira_id = jira_keys_and_ids[jira_key]
            try:
                success, clean_cache, failed_jira_keys = self.add_to_clean_cache(
                    sd_api,
                    jira_key,
                    failed_jira_keys,
                    clean_cache,
                    jira_id
                )
            except Exception as err:
                print(str(err) + "; with Ticket " + jira_key)
                self.add_lost_jira_key(jira_key)
                self.remove_jira_key(jira_key)
                success = False
        old_cache = self.load_cached_tickets()
        for jira_id in old_cache:
            if jira_id not in clean_cache:
                clean_cache[jira_id] = old_cache[jira_id]
        cache_file = self.environment.get_path_cache()
        file = open(cache_file, "wb")
        pickle.dump(clean_cache, file)
        return failed_jira_keys, success

    def post_progress(self, current, total):
        max_bars = 100
        progress = current / total
        percentage = int(round(progress * 100))
        current_bars = int(round(progress * max_bars, 0))
        diff_bars = max_bars - current_bars
        bars = '=' * current_bars
        diff = ' ' * diff_bars
        os.system('cls' if os.name == 'nt' else 'clear')
        os.system("echo [{}{}] {}%".format(bars, diff, percentage))
        os.system("echo {} of {} ids processed".format(current, total))

    def add_to_clean_cache(self, sd_api, jira_key, failed_jira_keys, clean_cache, jira_id):
        success = True
        try:
            raw_ticket_data = sd_api.request_ticket_data(jira_key)
            mapped_ticket = self.mapper.get_mapped_ticket(raw_ticket_data)
            mapped_ticket = self.mapper.format_related_tickets(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_status(mapped_ticket)
            mapped_ticket = self.mapper.format_status_history(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_worklog(mapped_ticket)
            mapped_ticket, worklog_persons = self.mapper.format_worklog(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_sla(mapped_ticket)
            mapped_ticket = self.mapper.format_sla(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_comments(mapped_ticket)
            mapped_ticket, comment_persons = self.mapper.format_comments(mapped_ticket)
            mapped_ticket = self.mapper.format_reporter(mapped_ticket)
            mapped_ticket = self.mapper.add_persons(mapped_ticket, (worklog_persons + comment_persons))
        except Exception as e:
            self.add_log_entry(self.__class__.__name__, e)
            failed_jira_keys.append(jira_key)
            success = False
            return success
        time.sleep(0.5)
        clean_cache[str(jira_id)] = mapped_ticket
        return success, clean_cache, failed_jira_keys

    def backup(self):
        cache_file = self.environment.get_path_cache()
        git_file = self.environment.get_path_git_cache()
        confluence_file = self.environment.get_path_confluence_cache()
        copyfile(cache_file, "{}.backup".format(cache_file))
        copyfile(git_file, "{}.backup".format(git_file))
        copyfile(confluence_file, "{}.backup".format(confluence_file))

    def add_log_entry(self, code_reference, message):
        log_file = self.environment.get_path_log()
        now = datetime.datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        entry = "{}: {} - {}\n".format(current_time, code_reference, message)
        file = open(log_file, "a")
        file.write(entry)
        file.close()

    def update_all_commits(self, git_api):
        commits = git_api.request_all_commits(self)
        success = len(commits) > 0

        return success

    def load_cached_commits(self):
        cache_file = self.environment.get_path_git_cache()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        return content

    def store_commits(self, commits):
        cache_file = self.environment.get_path_git_cache()
        file = open(cache_file, "wb")
        pickle.dump(commits, file)

    def store_documents(self, documents):
        cache_file = self.environment.get_path_confluence_cache()
        file = open(cache_file, "wb")
        pickle.dump(documents, file)

    def update_all_documents(self, confluence_api):
        documents = confluence_api.request_all_documents(self)
        success = len(documents) > 0

        return success

    def load_cached_documents(self):
        cache_file = self.environment.get_path_confluence_cache()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        return content

    def add_to_todays_score(self, jira_key, ticket_score):
        cache_file = self.environment.get_path_score()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        today = datetime.date.today().strftime("%Y%m%d")
        if today not in content:
            content[today] = {}
        content[today][jira_key] = ticket_score
        file = open(cache_file, "wb")
        pickle.dump(content, file)
        return numpy.sum(numpy.array(list(content[today].values())).astype(int))

    def get_high_score(self):
        cache_file = self.environment.get_path_score()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        highest_score = 0
        highest_day = ''
        for day in content:
            if isinstance(content[day], dict):
                day_sum = numpy.sum(numpy.array(list(content[day].values())).astype(int))
                if day_sum > highest_score:
                    highest_score = day_sum
                    highest_day = day
        return highest_day, highest_score
