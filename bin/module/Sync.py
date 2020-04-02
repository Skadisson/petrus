from bin.service import Cache
from bin.service import ServiceDeskAPI
import time


class Sync:
    """Synchronizes Cache with Jira SD API"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()

    def run(self):
        failed_jira_keys = []
        success = True

        start = float(time.time())

        try:
            failed_jira_keys, success = self.cache.sync(self.sd_api)
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)
            success = False

        stop = float(time.time())
        minutes = (stop - start) / 60
        if success:
            state = 'successfully'
        else:
            state = 'unsuccessfully'
        print('--- Synchronization with Jira SD API {} completed after {} minutes ---'.format(state, minutes))

        return failed_jira_keys, success
