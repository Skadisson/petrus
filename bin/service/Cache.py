from bin.service import Environment
import pickle
import os


class Cache:
    """Cache handler"""

    def __init__(self):
        self.environment = Environment.Environment()

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
            content[jira_id] = ticket
            file = open(cache_file, "wb")
            pickle.dump(content, file)
        return is_valid

    def load_jira_id_for_key(self, jira_key):
        jira_key_path = self.environment.get_path_jira_key()
        file_exists = os.path.exists(jira_key_path)
        if file_exists:
            file = open(jira_key_path, "rb")
            content = pickle.load(file)
            return content[jira_key]

        return None

    def load_jira_key_for_id(self, jira_id):
        jira_key_path = self.environment.get_path_jira_key()
        file_exists = os.path.exists(jira_key_path)
        if file_exists:
            file = open(jira_key_path, "rb")
            content = pickle.load(file)
            for content_id, key in content.items():
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
        content[jira_key] = jira_id
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
