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
        ticket_opened_calendar = analyze.ticket_opened_calendar(tickets)
        ticket_closed_calendar = analyze.ticket_closed_calendar(tickets)
        items = [{
            'ticket_count': len(tickets),
            'ticket_opened_calendar': ticket_opened_calendar,
            'ticket_closed_calendar': ticket_closed_calendar
        }]

        return items, success
