from bin.service import Cache


class CacheOP:
    """Cache Operator"""

    def __init__(self, jira_key):
        self.cache = Cache.Cache()
        self.jira_key = jira_key

    def run(self):
        items = []
        success = True
        cache = Cache.Cache()
        jira_id = cache.load_jira_id_for_key(self.jira_key)
        if jira_id is not None:
            tickets = cache.load_cached_tickets()
            ticket = cache.load_cached_ticket(jira_id)
            items.append({
                'count': len(tickets),
                'ticket': ticket
            })
        return items, success
