from bin.service import Analyze


class Trend:
    """Trend calculator"""

    def __init__(self, months):
        self.months = float(months)

    def run(self):
        success = True
        hours_per_project = None
        hours_total = None
        ticket_count = None
        hours_per_type = None

        try:
            analyze = Analyze.Analyze()
            days = self.months * 30
            hours_per_project = analyze.hours_per_project(days)
            hours_per_type = analyze.hours_per_type(days)
            hours_total = analyze.hours_total(days)
            ticket_count = analyze.ticket_count(days)
        except Exception as e:
            print(e)
            success = False

        items = [{
            'ticket_count': ticket_count,
            'hours_total': hours_total,
            'hours_per_projects': hours_per_project,
            'hours_per_type': hours_per_type
        }]
        return items, success
