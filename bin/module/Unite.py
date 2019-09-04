from bin.service import Cache
from bin.service import ServiceDeskAPI


class Unite:
    """Uniting Tickets across all Boards"""

    def __init__(self, jira_key="", method="", target_jira_key=""):
        self.jira_key = jira_key
        self.method = method
        self.target_jira_key = target_jira_key
        self.cache = Cache.Cache()
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()
        self.methods = {"help": [], "link": ["jira_key", "target_jira_key"], "unlink": ["jira_key", "target_jira_key"]}

    def run(self):
        success = True
        items = []

        if self.method in self.methods:
            if self.method == "help":
                response = {
                    "methods": self.methods,
                    "keys": self.cache.load_jira_keys_and_ids()
                }
                items.append(response)

        return items, success
