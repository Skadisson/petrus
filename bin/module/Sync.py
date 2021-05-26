from bin.service import Cache
from bin.service import ServiceDeskAPI
import time
import _thread
import threading


class Sync:
    """Synchronizes Cache with Jira SD API"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()

    def run(self):
        try:
            print('--- Synchronization with Jira started ---')
            _thread.start_new_thread(self.cache.sync, (self.sd_api, ))
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)

        while threading.active_count():
            pass
