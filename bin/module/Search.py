from bin.service import Cache
from bin.service import Context
from bin.service import LangChainOllama
from bin.module import Estimate


class Search:
    """Context search"""

    def __init__(self, keywords):
        self.cache = Cache.Cache()
        self.context = Context.Context()
        self.ollama = LangChainOllama.LangChainOllama()
        self.keywords = keywords

    def run(self):
        formatted_keywords = self.format_keywords()
        if len(formatted_keywords) == 1:
            mod_estimate = Estimate.Estimate(formatted_keywords[0])
            items, success = mod_estimate.run()
        elif len(formatted_keywords) > 2 and f"{formatted_keywords[0]}".lower() == 'ollama':
            items, success = self.ollama.ask_confluence(formatted_keywords[1:])
        elif len(formatted_keywords) > 1:
            tickets = self.cache.load_cached_tickets('SERVICE', True)
            relevancy, suggested_keys, similarities = self.context.calculate_relevancy_for_tickets(tickets, {'Keywords': formatted_keywords, 'Related': []})
            items = [{
                'relevancy': relevancy,
                'keywords': formatted_keywords,
                'similarities': similarities
            }]
        else:
            items = [{
                'relevancy': [],
                'keywords': formatted_keywords,
                'similarities': []
            }]

        success = True
        return items, success

    def format_keywords(self):
        formatted_keyword_string = self.keywords.replace(" ", ",")
        formatted_keywords = formatted_keyword_string.split(",")
        formatted_keywords = list(filter(None, formatted_keywords))
        return formatted_keywords
