from bin.service import Cache
from bin.service import Analyze


class Info:
    """Basic Information on Petrus"""

    @staticmethod
    def run():
        success = True
        cache = Cache.Cache()
        analyze = Analyze.Analyze()
        tickets = cache.load_cached_tickets()
        ticket_type_calendar = analyze.ticket_type_calendar(tickets)
        items = [{
            'ticket_count': len(tickets),
            'ticket_type_calendar': ticket_type_calendar
        }]

        return items, success
