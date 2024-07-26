from bin.service import Cache
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
import time


class LangChainOllama:

    def __init__(self):
        self.model_name = "llama3.1:8b"
        self.chain_type = "stuff"
        self.llm = Ollama(model=self.model_name)
        self.cache = Cache.Cache()

    def generate_summaries(self, tickets):
        summaries = []
        for ticket in tickets:
            if 'Summary' not in ticket:
                while True:
                    every_five_minutes = int(time.time()) % (5*60) == 0
                    if every_five_minutes:
                        start = time.time()
                        documents = [Document(self.promptify_ticket(ticket))]
                        chain = self.init_chain()
                        result = chain.invoke(documents)
                        ticket['Summary'] = result['output_text']
                        summaries.append(f"{ticket['Key']}: {ticket['Summary']}")
                        is_stored = self.cache.store_ticket(ticket['ID'], ticket)
                        if is_stored is False:
                            self.cache.add_log_entry(self.__class__.__name__, str(f"Could not build and store summary for ticket with ID {ticket['ID']}"))
                        else:
                            minutes = round((time.time() - start) / 60, 2)
                            current_time = self.cache.get_current_time()
                            print(f">>> {current_time}: Completed Summary for Ticket {ticket['Key']} after {minutes} minutes.")
                        break

        return summaries

    def generate_general_summary(self, tickets):
        summaries = []
        for ticket in tickets:
            if 'Key' in ticket and 'Time_Spent' in ticket and ticket['Time_Spent'] is not None and 'Summary' in ticket and ticket['Summary'] != '':
                summaries.append(f"{ticket['Key']}: {ticket['Summary']}")

        documents = [Document(self.promptify_summaries(summaries))]
        chain = self.init_chain()
        result = chain.invoke(documents)

        return result['output_text']

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

    @staticmethod
    def promptify_summaries(summaries):
        text = ("Please summarize the following Jira ticket summaries into one general recap of what kind of issues "
                "have been brought up and what systems have been the ones with the highest frequency of issues:")
        for summary in summaries:
            text += "\n"
            text += '-' * 20
            text += "\n"
            text += f"{summary}"
        return text

    def train_my_llama(self, tickets):
        target_model_name = 'my_llama'
        documents = []
        for ticket in tickets:
            if 'Summary' in ticket and ticket['Summary'] != '':
                documents.append(
                    Document(f"Jira Ticket Key: {ticket['Key']}; Jira Ticket Summary: {ticket['Summary']}")
                )
        current_time = self.cache.get_current_time()
        print(f">>> {current_time}: Starting to train '{target_model_name}' model using '{self.model_name}' for {len(documents)} tickets.")
        start = time.time()
        try:
            self.llm.train(documents)
            self.llm.save(target_model_name)
            minutes = round((time.time() - start) / 60, 2)
            current_time = self.cache.get_current_time()
            print(f">>> {current_time}: Successfully trained '{target_model_name}' model using '{self.model_name}' after {minutes} minutes.")
        except Exception as e:
            minutes = round((time.time() - start) / 60, 2)
            current_time = self.cache.get_current_time()
            print(f">>> {current_time}: Failed to train '{target_model_name}' model using '{self.model_name}' after {minutes} minutes. Error message: '{e}'")
