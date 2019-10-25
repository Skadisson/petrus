from bin.service import Cache


class Info:
    """Basic Information on Petrus"""

    @staticmethod
    def run():
        success = True
        cache = Cache.Cache()
        tickets = cache.load_cached_tickets()
        items = [{
            'ticket_count': len(tickets)
        }]

        return items, success
