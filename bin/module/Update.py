from bin.service import Cache
from bin.service import ServiceDeskAPI


class Update:
    """Cache Updater"""

    @staticmethod
    def run():
        cache = Cache.Cache()
        sd_api = ServiceDeskAPI.ServiceDeskAPI()
        failed_jira_keys, success = cache.update_all_tickets(sd_api)
        return failed_jira_keys, success
