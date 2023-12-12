from bin.service import Cache
import pandas


class OpenTickets:
    """OpenTickets filter"""

    def __init__(self, project="SERVICE"):
        self.project = str(project)
        self.cache = Cache.Cache()

    def run(self):
        success = True
        try:
            open_tickets = list(self.cache.get_open_tickets(self.project))
            df_ot = pandas.DataFrame(open_tickets)
            df_ot.to_csv(path_or_buf='temp/ots.csv', sep=';', encoding='utf-8')
        except Exception as e:
            success = False
        items = [{
            'path': 'temp/ots.csv',
            'success': success
        }]
        return items, success
