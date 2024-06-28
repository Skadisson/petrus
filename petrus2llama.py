from bin.service import LangChainOllama


if __name__ == '__main__':
    try:
        from bin.service import Cache
        cache = Cache.Cache()
        tickets = cache.load_cached_tickets(project='SERVICE', only_worked_on=True)
        tickets = sorted(tickets, key=lambda ticket: ticket['Created'], reverse=True)
        lcOllama = LangChainOllama.LangChainOllama()
        summaries = lcOllama.generate_summaries(tickets)
        print(summaries)
    except Exception as e:
        print(e)
