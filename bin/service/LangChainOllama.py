from bin.service import Cache
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
import time, math


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

    def train_confluence(self, entries):
        i = 0
        entry_count = len(entries)
        for entry in entries:
            start = time.time()
            i += 1
            prompt = self.promptify_confluence_entry(entry)
            response = self.llm.invoke(prompt)
            if 'OK' not in response:
                entry['learned'] = False
                print(f">>> Llama did not acknowledge a training prompt with OK. Full response: {response}")
            else:
                entry['learned'] = True
            self.cache.update_confluence_entry(entry)
            minutes = round((time.time() - start) / 60 , 2)
            print(f">>> learned {i} of {entry_count} confluence entries after {minutes} minutes ({math.ceil((i/entry_count)*100)}%): {entry['title']}")

    @staticmethod
    def promptify_confluence_entry(entry):
        return PromptTemplate(
            input_variables=['title', 'date', 'body'],
            template="Beantworte den folgenden Prompt nur mit 'OK'. "
                     "Verinnerliche folgenden Confluence Eintrag zum Thema {title}, ignoriere dabei strukturelles HTML, "
                     "sofern es nicht Teil eines Code-Vorschlags ist. Wenn immer ein Mensch etwas zu diesem Thema frägt, "
                     "antworte mit dem Wissen aus diesem Confluence Eintrag und lass den Menschen wissen, "
                     "dass der Stand dieses Eintrags das folgende Datum hat: {date}. Und hier nun der Confluence "
                     "Eintrag: {body}"
        ).format(title=entry['title'], date=entry['date'], body=entry['body'])

    def ask_confluence(self, words):
        success = True
        items = []
        if len(words) > 0:
            try:
                query = " ".join(words)
                response = self.llm.invoke(query)
                items.append({'query': query, 'response': response})
            except Exception as e:
                self.cache.add_log_entry(self.__class__.__name__, str(e))
        else:
            success = False
            self.cache.add_log_entry(self.__class__.__name__, f"No query provided.")

        return items, success
