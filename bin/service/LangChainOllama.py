from bin.service import Cache
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document


class LangChainOllama:

    def __init__(self):
        self.model_name = "llama3:8b"
        self.chain_type = "stuff"
        self.llm = Ollama(model=self.model_name)
        self.cache = Cache.Cache()

    def generate_summary(self, ticket):

        text = self.promptify_ticket(ticket)
        chain = self.init_chain()
        result = chain.invoke([Document(text)])
        ticket['Summary'] = result['output_text']
        is_stored = self.cache.store_ticket(ticket['ID'], ticket)
        if is_stored is False:
            self.cache.add_log_entry(self.__class__.__name__, str(f"Could not build and store summary for ticket with ID {ticket['ID']}"))

        return is_stored

    def generate_summaries(self, tickets):
        summaries = []
        for ticket in tickets:
            if 'Summary' not in ticket:
                documents = [Document(self.promptify_ticket(ticket))]
                chain = self.init_chain()
                result = chain.invoke(documents)
                ticket['Summary'] = result['output_text']
                summaries.append(f"{ticket['Key']}: {ticket['Summary']}")
                is_stored = self.cache.store_ticket(ticket['ID'], ticket)
                if is_stored is False:
                    self.cache.add_log_entry(self.__class__.__name__, str(f"Could not build and store summary for ticket with ID {ticket['ID']}"))
                    break

        return summaries

    def init_chain(self):
        return load_summarize_chain(self.llm, chain_type=self.chain_type)

    @staticmethod
    def promptify_ticket(ticket):
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

        return text
