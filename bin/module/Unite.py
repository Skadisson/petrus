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
                    "mirrors": self.cache.load_mirrors()
                }
                items.append(response)
            if self.method == "link":
                if self.jira_key != "" and self.target_jira_key != "":
                    self.cache.add_mirror(self.jira_key, self.target_jira_key)
                    response = {
                        "mirrors": self.cache.load_mirrors()
                    }
                    items.append(response)
                else:
                    response = {
                        "methods": self.methods
                    }
                    items.append(response)
                    success = False
            if self.method == "unlink":
                if self.jira_key != "" and self.target_jira_key != "":
                    self.cache.remove_mirror(self.jira_key, self.target_jira_key)
                    response = {
                        "mirrors": self.cache.load_mirrors()
                    }
                    items.append(response)
                else:
                    response = {
                        "methods": self.methods
                    }
                    items.append(response)
                    success = False

        return items, success
