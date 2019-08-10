from bin.service import ServiceDeskAPI
from bin.service import Map
from bin.service import Cache
from bin.service import Context
from bin.service import SciKitLearn


class Estimate:
    """Estimator"""

    def __init__(self, jira_key):
        self.jira_key = jira_key
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()
        self.mapper = Map.Map()
        self.cache = Cache.Cache()
        self.context = Context.Context()
        self.sci_kit = SciKitLearn.SciKitLearn()

    def run(self):
        try:
            ticket_data = self.sd_api.request_ticket_data(self.jira_key)
            if ticket_data is None:
                estimation = None
                success = False
            else:
                mapped_ticket = self.mapper.get_mapped_ticket(ticket_data)
                success = self.cache.store_ticket(self.jira_key, mapped_ticket)
                cached_tickets = self.cache.load_cached_tickets()
                relevancy = self.context.calculate_relevancy_for_tickets(cached_tickets, mapped_ticket['Keywords'])
                normalized_ticket = self.mapper.normalize_ticket(mapped_ticket)
                similar_tickets, hits = self.context.filter_similar_tickets(relevancy, cached_tickets, self.jira_key)
                if hits > 0:
                    estimation = self.sci_kit.estimate(normalized_ticket, similar_tickets, 'Time_Spent', ['Relevancy', 'Priority', 'Type', 'Organization'])
                else:
                    estimation = None
                    success = False
        except Exception as e:
            print(e)
            mapped_ticket = None
            success = False
            estimation = None
            hits = None

        items = [{
            'ticket': mapped_ticket,
            'estimation': estimation,
            'hits': hits
        }]
        return items, success
