from bin.service import Analyze
from bin.service import Cache


class Rank:
    """Rank Operator"""

    def __init__(self, jira_key):
        self.analyze = Analyze.Analyze()
        self.cache = Cache.Cache()
        self.jira_key = jira_key

    def run(self):
        items = []
        success = False
        jira_id = self.cache.load_jira_id_for_key(self.jira_key)
        if jira_id is not None:
            success = True
            tickets = self.cache.load_cached_tickets()
            ticket = tickets[jira_id]
            rank = self.analyze.rank_ticket(ticket, tickets)
            items.append({
                'rank': rank,
                'ticket': ticket
            })
        return items, success

