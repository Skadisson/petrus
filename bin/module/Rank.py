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
            ticket = self.cache.load_cached_ticket(jira_id)
            score = self.analyze.rank_ticket(ticket)
            items.append({
                'score': score,
                'ticket': ticket
            })
        return items, success

