from bin.service import ServiceDeskAPI
from bin.service import Map
from bin.service import Cache


class Estimate:
    """Estimator"""

    def __init__(self, jira_key):
        self.jira_key = jira_key
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()
        self.mapper = Map.Map()
        self.cache = Cache.Cache()

    def run(self):
        try:
            ticket_data = self.sd_api.request_ticket_data(self.jira_key)
            mapped_ticket = self.mapper.get_mapped_ticket(ticket_data)
            success = self.cache.store_ticket(self.jira_key, mapped_ticket)
        except Exception:
            mapped_ticket = None
            success = False

        items = [{
            'ticket': mapped_ticket
        }]
        return items, success
