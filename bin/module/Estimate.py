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

    def retrieve_ticket(self):
        ticket_data = self.sd_api.request_ticket_data(self.jira_key)
        mapped_ticket = self.mapper.get_mapped_ticket(ticket_data)
        mapped_ticket = self.mapper.format_related_tickets(mapped_ticket)
        mapped_ticket = self.sd_api.request_ticket_status(mapped_ticket)
        mapped_ticket = self.mapper.format_status_history(mapped_ticket)
        mapped_ticket = self.sd_api.request_ticket_worklog(mapped_ticket)
        mapped_ticket = self.mapper.format_worklog(mapped_ticket)
        mapped_ticket = self.sd_api.request_ticket_comments(mapped_ticket)
        mapped_ticket = self.mapper.format_comments(mapped_ticket)
        mapped_ticket = self.mapper.format_reporter(mapped_ticket)
        return mapped_ticket

    def format_tickets(self, mapped_ticket):
        cached_tickets = self.cache.load_cached_tickets()
        relevancy = self.context.calculate_relevancy_for_tickets(cached_tickets, mapped_ticket)
        normalized_ticket = self.mapper.normalize_ticket(mapped_ticket)
        similar_tickets, hits = self.context.filter_similar_tickets(
            relevancy,
            cached_tickets,
            mapped_ticket['ID']
        )
        return normalized_ticket, similar_tickets, hits

    def run(self):
        mapped_ticket = None
        success = False
        estimation = None
        hits = None
        normalized_ticket = None

        try:
            if self.jira_key is not None:
                mapped_ticket = self.retrieve_ticket()
                jira_id = str(mapped_ticket['ID'])
                self.cache.store_jira_key_and_id(self.jira_key, jira_id)
                success = self.cache.store_ticket(jira_id, mapped_ticket)
                if success:
                    normalized_ticket, similar_tickets, hits = self.format_tickets(mapped_ticket)
                    if hits == 0:
                        estimation = 900
                    else:
                        estimation = self.sci_kit.estimate(
                            normalized_ticket,
                            similar_tickets,
                            'Time_Spent',
                            ['Relevancy', 'Key', 'Priority', 'State_Changes', 'Type', 'Organization']
                        )
                    success = self.sd_api.update_ticket_times(jira_id, estimation, mapped_ticket)
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)

        if estimation is not None:
            estimation = float(estimation)
        items = [{
            'ticket': mapped_ticket,
            'estimation': estimation,
            'hits': hits,
            'normal_ticket': normalized_ticket
        }]
        return items, success
