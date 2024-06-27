from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document


if __name__ == '__main__':
    try:
        from bin.service import Cache
        cache = Cache.Cache()
        tickets = cache.load_cached_tickets(project='SERVICE', only_worked_on=True)
        tickets = sorted(tickets, key=lambda ticket: ticket['Created'], reverse=True)

        for ticket in tickets:
            if "Summary" in ticket or ticket['ID'] is None or ticket['Key'] is None:
                continue

            text = ""
            for param in ["Key", "Title", "Text", "Project"]:
                if ticket[param] is not None:
                    text += f"{param}: {ticket[param]}; "
            if len(ticket['Related']) > 0:
                text += f"Related Keys: {', '.join(ticket['Related'])}; "
            if ticket['Notes'] is not None:
                text += f"Notes: {ticket['Notes']}; "
            for comment in ticket["Comments"]:
                text += f"Comment: {comment}; "
            docs = [Document(text)]

            llm = Ollama(model="llama3:8b")
            chain = load_summarize_chain(llm, chain_type="stuff")

            result = chain.invoke(docs)
            ticket['Summary'] = result['output_text']
            print(f"{ticket['Key']}: {ticket['Summary']}")
            is_stored = cache.store_ticket(ticket['ID'], ticket)
            if is_stored:
                print("stored")
            else:
                print("rejected")
    except Exception as e:
        print(e)
