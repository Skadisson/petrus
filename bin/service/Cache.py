from bin.service import Environment
from bin.service import Map
import pymongo
import pickle
import os
import datetime
import numpy
import re
import time


class Cache:
    """Cache handler"""

    def __init__(self):
        self.environment = Environment.Environment()
        self.mapper = Map.Map()
        self.client = pymongo.MongoClient()
        self.database = self.client.petrus
        self.table_cache = self.database.cache
        self.table_jira_keys = self.database.jira_keys
        self.table_score = self.database.high_score
        self.table_comments = self.database.comments
        self.add_text_indices()

    def add_text_indices(self):
        self.table_cache.create_index([('Key', pymongo.TEXT)])

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
            stored_ticket = self.table_cache.find_one({'ID': jira_id})
            if stored_ticket is not None:
                self.table_cache.replace_one({'ID': jira_id}, ticket)
            else:
                self.table_cache.insert_one(ticket)
        return is_valid

    def get_all_jira_keys(self):
        return list(self.table_cache.distinct('Key'))

    def load_jira_id_for_key(self, jira_key):
        stored_relation = self.table_jira_keys.find_one({'key': jira_key})
        if stored_relation is not None:
            return stored_relation['id']

        return None

    def load_jira_key_for_id(self, jira_id):
        stored_relation = self.table_jira_keys.find_one({'id': jira_id})
        if stored_relation is not None:
            return stored_relation['key']

        return None

    def store_jira_key_and_id(self, jira_key, jira_id):
        relation = {'id': jira_id, 'key': jira_key}
        stored_relation = self.table_jira_keys.find_one(relation)
        if stored_relation is None:
            stored_relation = relation
            stored_relation['frequency'] = 'high'
            self.table_jira_keys.insert_one(stored_relation)
        else:
            stored_relation['frequency'] = 'low'
            self.table_jira_keys.replace_one(relation, stored_relation)

    @staticmethod
    def validate_ticket_data(ticket_data):
        for i in ticket_data:
            is_valid = ticket_data[i] is not None
            if is_valid:
                return True
        return False

    def load_cached_tickets(self, project='SERVICE'):
        rgx = re.compile(f"{project}.*", re.IGNORECASE)
        return self.table_cache.find({'Key': {'$regex': rgx}})

    def load_cached_tickets_except(self, ticket_key, project='SERVICE'):
        rgx = re.compile(f"{project}.*", re.IGNORECASE)
        return self.table_cache.find({'Key': {'$regex': rgx, '$ne': ticket_key}, 'Time_Spent': {'$gt': 0}})

    def count_tickets(self):
        return self.table_cache.count()

    def load_cached_ticket(self, jira_id):
        return self.table_cache.find_one({'ID': jira_id})

    def load_jira_keys_and_ids(self):
        return self.table_jira_keys.find()

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
        self.table_jira_keys.delete_one({'key': jira_key})

    def parallel_sync(self):
        """TBI"""

    def sync(self, sd_api):
        clean_cache = {}
        failed_jira_keys = []
        ticket_total = 0

        max_results = 100

        leftover_keys = self.get_all_jira_keys()
        new_keys = []
        start = time.time()

        projects = self.environment.get_service_projects()
        for project in projects:
            offset = 0
            jira_keys = sd_api.request_service_jira_keys(offset, max_results, project)
            while len(jira_keys) > 0:
                ticket_total += len(jira_keys)
                for jira_id in jira_keys:
                    jira_key = jira_keys[jira_id]
                    is_old_key = jira_key in leftover_keys
                    if is_old_key:
                        leftover_keys.remove(jira_key)
                        self.store_jira_key_and_id(jira_key, jira_id)
                    else:
                        new_keys.append(jira_key)
                        try:
                            success, clean_cache, failed_jira_keys = self.add_to_clean_cache(
                                sd_api,
                                jira_key,
                                failed_jira_keys,
                                clean_cache,
                                jira_id
                            )
                            if success:
                                self.store_jira_key_and_id(jira_key, jira_id)
                        except Exception as err:
                            print(str(err) + "; with Ticket " + jira_key)
                            self.add_lost_jira_key(jira_key)
                            self.remove_jira_key(jira_key)
                synced_current = len(clean_cache)
                self.update_cache_diff(clean_cache)
                print('>>> successfully synced {} new or updated tickets out of {} total in project "{}"'.format(synced_current, ticket_total, project))
                offset += max_results
                jira_keys = sd_api.request_service_jira_keys(offset, max_results, project)
        synced_current = len(clean_cache)
        hours = round((time.time() - start) / 60 / 60, 2)
        print('>>> completed syncing {} new or updated tickets out of {} total after {} hours'.format(synced_current, ticket_total, hours))
        self.add_jira_log_entry(self.__class__.__name__, f"{ticket_total} tickets processed after {hours} hours, {len(new_keys)} of those were new tickets")
        if len(leftover_keys) > 0:
            self.add_jira_log_entry(self.__class__.__name__, f"Following tickets seem to have been deleted: {', '.join(leftover_keys)}")

    def update_cache_diff(self, clean_cache):
        for jira_id in clean_cache:
            ticket = clean_cache[jira_id]
            stored = self.store_ticket(jira_id, ticket)
            if stored is False:
                print('>>> ticket with id {} couldnt be stored'.format(jira_id))

    def add_to_clean_cache(self, sd_api, jira_key, failed_jira_keys, clean_cache, jira_id):
        success = True
        try:
            last_updated = None
            cached_ticket = self.load_cached_ticket(jira_id)
            if cached_ticket is not None and 'Updated' in cached_ticket and cached_ticket['Updated'] is not None:
                last_updated = cached_ticket['Updated']
            raw_ticket_data = sd_api.request_ticket_data(jira_key)
            mapped_ticket = self.mapper.get_mapped_ticket(raw_ticket_data)
            if last_updated is not None and 'Updated' in mapped_ticket and mapped_ticket['Updated'] is not None:
                if last_updated == mapped_ticket['Updated']:
                    return True, clean_cache, failed_jira_keys
            mapped_ticket = self.mapper.format_related_tickets(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_status(mapped_ticket)
            mapped_ticket = self.mapper.format_status_history(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_worklog(mapped_ticket)
            mapped_ticket, worklog_persons = self.mapper.format_worklog(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_sla(mapped_ticket)
            mapped_ticket = self.mapper.format_sla(mapped_ticket)
            mapped_ticket = sd_api.request_ticket_comments(mapped_ticket)
            mapped_ticket, comment_persons = self.mapper.format_comments(mapped_ticket)
            mapped_ticket = self.mapper.format_text(mapped_ticket)
            mapped_ticket = self.mapper.format_reporter(mapped_ticket)
            mapped_ticket = self.mapper.add_persons(mapped_ticket, (worklog_persons + comment_persons))
            mapped_ticket = self.mapper.format_versions(mapped_ticket)
        except Exception as e:
            self.add_log_entry(self.__class__.__name__, e)
            failed_jira_keys.append(jira_key)
            success = False
            return success
        clean_cache[str(jira_id)] = mapped_ticket
        return success, clean_cache, failed_jira_keys

    def add_log_entry(self, code_reference, message):
        log_file = self.environment.get_path_log()
        now = datetime.datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        entry = "{}: {} - {}\n".format(current_time, code_reference, message)
        file = open(log_file, "a")
        file.write(entry)
        file.close()

    def add_jira_log_entry(self, code_reference, message):
        log_file = self.environment.get_path_jira_log()
        now = datetime.datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        entry = "{}: {} - {}\n".format(current_time, code_reference, message)
        file = open(log_file, "a")
        file.write(entry)
        file.close()

    def add_to_todays_score(self, jira_key, ticket_score):

        today = datetime.date.today().strftime("%Y%m%d")
        stored_score = self.table_score.find_one({'day': today})
        if stored_score is None:
            self.table_score.insert_one({
                'day': today,
                'scores': {
                    jira_key: ticket_score
                }
            })
            stored_score = self.table_score.find_one({'day': today})

        stored_score['scores'][jira_key] = ticket_score
        self.table_score.replace_one({'day': today}, stored_score)
        total_score = self.calculate_score(stored_score)

        return total_score

    @staticmethod
    def calculate_score(stored_score):
        return numpy.sum(
            numpy.array(
                list(stored_score['scores'].values())
            ).astype(int)
        )

    def get_high_score(self):
        highest_score = 0
        highest_day = ''

        all_scores = self.table_score.find()
        for score in all_scores:
            day_score = self.calculate_score(score)
            if day_score > highest_score:
                highest_score = day_score
                highest_day = score['day']
        return highest_day, highest_score

    def get_monthly_top_score(self):
        monthly_score = {}

        all_scores = self.table_score.find()
        for score in all_scores:
            month = score['day'][0:6]
            day_score = self.calculate_score(score)
            if month not in monthly_score:
                monthly_score[month] = int(day_score)
            else:
                monthly_score[month] += int(day_score)

        return max(monthly_score), monthly_score

    def comment_exists(self, jira_id):
        comment = self.table_comments.find_one({'jira_id': jira_id})
        return comment is not None

    def store_comment(self, jira_id, comment):
        self.table_comments.insert_one({'jira_id': jira_id, 'comment': comment})
