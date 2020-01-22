from bin.service import Cache
from bin.service import ServiceDeskAPI
from bin.service import GitlabAPI
from bin.service import ConfluenceAPI
import time


class Update:
    """Cache Updater"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()
        self.git_api = GitlabAPI.GitlabAPI()
        self.confluence_api = ConfluenceAPI.ConfluenceAPI()

    def run(self):
        failed_jira_keys = []
        try:

            start = float(time.strftime('%S'))

            print('--- Updating Jira Cache [1/3] ---')
            failed_jira_keys, success = self.cache.update_all_tickets(self.sd_api)
            if success:
                print('DONE')
            else:
                print('FAILED')

            print('--- Updating Git Cache [2/3] ---')
            success = self.cache.update_all_commits(self.git_api)
            if success:
                print('DONE')
            else:
                print('FAILED')

            print('--- Updating Confluence Cache [3/3] ---')
            success = self.cache.update_all_documents(self.confluence_api)
            if success:
                print('DONE')
            else:
                print('FAILED')

            stop = float(time.strftime('%S'))
            minutes = (stop - start) / 60
            if success:
                state = 'successfully'
            else:
                state = 'unsuccessfully'
            print('--- Update {} Completed after {} minutes ---'.format(state, minutes))

        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)
            success = False

        return failed_jira_keys, success
