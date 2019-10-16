from bin.service import Cache
from bin.service import Context


class Search:
    """Context search"""

    def __init__(self, keywords):
        self.cache = Cache.Cache()
        self.context = Context.Context()
        self.keywords = keywords

    def run(self):
        tickets = self.cache.load_cached_tickets()
        formatted_keywords = self.format_keywords()
        relevancy = self.context.calculate_relevancy_for_tickets(tickets, {'Keywords': formatted_keywords, 'Related': []})

        items = [{
            'relevancy': relevancy,
            'keywords': formatted_keywords
        }]
        success = True
        return items, success

    def format_keywords(self):
        formatted_keyword_string = self.keywords.replace(" ", ",")
        formatted_keywords = formatted_keyword_string.split(",")
        formatted_keywords = list(filter(None, formatted_keywords))
        return formatted_keywords
