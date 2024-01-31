from bin.service import Cache
from bin.service import JiraRestAPI
from bin.service import Context
import _thread
import threading


class Sync:
    """Synchronizes Cache with Jira SD API"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.sd_api = JiraRestAPI.JiraRestAPI()
        self.context = Context.Context()

    def run(self):
        try:
            print('--- Synchronization with Jira started ---')
            _thread.start_new_thread(self.cache.sync, (self.sd_api, self.context, ))
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)

        while threading.active_count():
            pass
