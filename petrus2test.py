from bin.service import Cache
from bin.service import Context
from bin.module import Estimate
import time


def format_keywords(keywords_):
    formatted_keyword_string = keywords_.replace(" ", ",")
    formatted_keywords = formatted_keyword_string.split(",")
    formatted_keywords = list(filter(None, formatted_keywords))
    return formatted_keywords


start = float(time.time())

cache = Cache.Cache()
context = Context.Context()
keywords = 'Die Print Template Regeln bei Weberhaus funktionieren nicht'
relevancy = []

tickets = cache.load_cached_tickets()
commits = cache.load_cached_commits()
documents = cache.load_cached_documents()
formatted_keywords = format_keywords(keywords)
if len(formatted_keywords) == 1:
    mod_estimate = Estimate.Estimate(formatted_keywords[0])
    items, success = mod_estimate.run()
elif len(formatted_keywords) > 1:
    relevancy = context.calculate_relevancy_for_tickets(tickets, {'Keywords': formatted_keywords, 'Related': []})
    try:
        relevancy = context.add_relevancy_for_commits(commits, formatted_keywords, relevancy)
        relevancy = context.add_relevancy_for_documents(documents, formatted_keywords, relevancy)
    except Exception as e:
        print(e)

stop = float(time.time())
minutes = (stop - start) / 60
print(relevancy)
print('--- Test completed after {} minutes ---'.format(minutes))
