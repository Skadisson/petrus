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
        mapped_ticket = None
        success = False
        estimation = None
        hits = None
        normalized_ticket = None

        try:
            if self.jira_key is not None:
                ticket_data = self.sd_api.request_ticket_data(self.jira_key)
                mapped_ticket = self.mapper.get_mapped_ticket(ticket_data)
                mapped_ticket = self.sd_api.request_ticket_status(self.jira_key, mapped_ticket)
                mapped_ticket = self.mapper.format_status_history(mapped_ticket)
                success = self.cache.store_ticket(self.jira_key, mapped_ticket)
                if success:
                    cached_tickets = self.cache.load_cached_tickets()
                    relevancy = self.context.calculate_relevancy_for_tickets(cached_tickets, mapped_ticket['Keywords'])
                    normalized_ticket = self.mapper.normalize_ticket(mapped_ticket)
                    similar_tickets, hits = self.context.filter_similar_tickets(relevancy, cached_tickets, self.jira_key)
                    if hits > 0:
                        estimation = self.sci_kit.estimate(normalized_ticket, similar_tickets, 'Time_Spent', ['Relevancy', 'Priority', 'Type', 'Organization'])
                        success = self.sd_api.update_ticket_times(self.jira_key, estimation, mapped_ticket)
                    else:
                        success = False
        except Exception as e:
            print(e)

        if mapped_ticket is not None:
            mapped_ticket['ID'] = int(mapped_ticket['ID'])
        if estimation is not None:
            estimation = float(estimation)
        items = [{
            'ticket': mapped_ticket,
            'estimation': estimation,
            'hits': hits,
            'normal_ticket': normalized_ticket
        }]
        return items, success
