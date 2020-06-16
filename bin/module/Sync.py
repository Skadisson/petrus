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
        success = True

        print('--- Synchronization with Jira started ---')
        start = float(time.time())

        try:
            _thread.start_new_thread(self.cache.sync, (self.sd_api, ))
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)
            success = False

        while threading.active_count():
            pass

        if success:
            state = 'successfully'
        else:
            state = 'unsuccessfully'

        stop = float(time.time())
        minutes = (stop - start) / 60
        print('--- Synchronization with Jira SD API {} completed after {} minutes ---'.format(state, minutes))
