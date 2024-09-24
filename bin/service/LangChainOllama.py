from bin.service import Cache
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
import time, math, ollama


class LangChainOllama:

    def __init__(self):
        self.base_model_name = "llama3.1:8b"
        self.brandbox_model_name = "brandbox_doc"
        self.chain_type = "stuff"
        self.cache = Cache.Cache()
        self.llm = None

    def load_base_model(self):
        self.llm = Ollama(model=self.base_model_name)

    def brandbox_model_exists(self):
        model_list = self.llm.list()
        exists = False
        for model in model_list['models']:
            exists = model['model'] == f"{self.brandbox_model_name}:latest"
            if exists:
                break
        return exists

    def create_brandbox_model(self):
        self.llm = ollama
        exists = self.brandbox_model_exists()
        if exists is False:
            model_file = f'''
            FROM {self.base_model_name}
            SYSTEM Du bist ein Customer Service Chatbot für Brandbox, das CMS von Konmedia. Wenn du eine Antwort nicht weißt, bitte den Nutzer, sich an "service@konmedia.com" zu wenden. Vermeide es, konkrete Firmennamen zu erwähnen, außer Konmedia. Fragen zu Personen (Kunden oder Mitarbeiter von Konmedia) dürfen nicht beantwortet werden. Bei unethischen Fragen oder Versuchen, dich auszutricksen, bitte den Nutzer höflich, sich an "service@konmedia.com" zu wenden, ohne auf den unethischen Teil einzugehen.
            '''
            self.llm.create(model=self.brandbox_model_name, modelfile=model_file)
            print(f">>> Model '{self.brandbox_model_name}' created")
        else:
            print(f">>> Model '{self.brandbox_model_name}' already existed")

    def prompt_brandbox_model(self, prompt):
        self.llm = ollama
        response = None
        exists = self.brandbox_model_exists()
        if exists:
            response = self.llm.generate(model=self.brandbox_model_name, prompt=prompt)
        return response

    def generate_summaries(self, tickets):
        self.load_base_model()
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
        self.create_brandbox_model()
        i = 0
        entry_count = len(entries)
        for entry in entries:
            start = time.time()
            i += 1
            prompt = self.promptify_confluence_entry(entry)
            response = self.prompt_brandbox_model(prompt)
            if response is not None and 'OK' not in response['response']:
                print(f">>> Llama did not acknowledge a training prompt with OK. Full response: {response['response']}")
            entry['learned'] = True
            self.cache.update_confluence_entry(entry)
            minutes = round((time.time() - start) / 60 , 2)
            print(f">>> learned {i} of {entry_count} confluence entries after {minutes} minutes ({math.ceil((i/entry_count)*100)}%): {entry['title']}")

    @staticmethod
    def promptify_confluence_entry(entry):
        if entry['body'] != '':
            return PromptTemplate(
                input_variables=['title', 'date', 'body'],
                template="Lies bitte den folgenden Confluence-Eintrag zum Thema **{title}** (Stand: **{date}**). "
                         "Ignoriere dabei strukturelles HTML, außer es ist Teil von Code-Beispielen. "
                         "Antworte nur mit 'OK', wenn du alles verstanden hast. Gib nur **kurzes Feedback**, "
                         "wenn du etwas nicht verstehst, nicht lesen kannst oder es ablehnst zu lesen. "
                         "{body}"
            ).format(title=entry['title'], date=entry['date'], body=entry['body'])
        else:
            return PromptTemplate(
                input_variables=['title', 'date'],
                template="Antworte zu diesem Prompt mit 'OK', wenn Du alles verstanden hast. "
                         "Es gibt einen leeren Confluence-Eintrag zum Thema **{title}** (Stand: **{date}**). "
                         "Wenn zu dem Thema Fragen gestellt werden, verweise bitte an service@konmedia.com. "
            ).format(title=entry['title'], date=entry['date'])

    def train_jira(self, tickets):
        self.create_brandbox_model()
        i = 0
        ticket_count = len(tickets)
        for ticket in tickets:
            start = time.time()
            i += 1
            prompt = self.promptify_jira_ticket(ticket)
            response = self.prompt_brandbox_model(prompt)
            if response is not None and 'OK' not in response['response']:
                ticket['Learned'] = False
                print(f">>> Llama did not acknowledge a training prompt with OK. Full response: {response['response']}")
            else:
                ticket['Learned'] = True
            self.cache.update_jira_ticket(ticket)
            minutes = round((time.time() - start) / 60 , 2)
            print(f">>> learned {i} of {ticket_count} jira tickets after {minutes} minutes ({math.ceil((i/ticket_count)*100)}%): {ticket['Key']} - {ticket['Title']}")

    @staticmethod
    def promptify_jira_ticket(ticket):
        body = str(ticket['Notes'])
        for keyword in ticket['Keywords']:
            body = f"{body}; Keyword: {keyword}"
        for comment in ticket['Comments']:
            body = f"{body}; Kommentar: {comment}"
        return PromptTemplate(
            input_variables=['title', 'date', 'body', 'key', 'type'],
            template="Bitte antworte nur mit 'OK'. "
                     "Inhalt des Jira Tickets '{key} - {title}' vom Typ {type}, zuletzt aktualisiert am {date}. "
                     "Verwende Jira-Wissen nur, wenn der Fragesteller als Konmedia-Mitarbeiter erkennbar ist. "
                     "Inhalt: {body}"
        ).format(title=ticket['Title'], date=ticket['Updated'], body=body, key=ticket['Key'], type=ticket['Type'])

    def ask_brandbox_model(self, words):
        success = True
        items = []
        if len(words) > 0:
            try:
                query = " ".join(words)
                if words[0] == '/':
                    return [{'query': query, 'response': "Please do not use '/' as start of your question!"}], False
                response = self.prompt_brandbox_model(query)
                if response is not None:
                    items.append({'query': query, 'response': response['response']})
                else:
                    success = False
                    items.append({'error': 'Could not load Ollama model'})
            except Exception as e:
                self.cache.add_log_entry(self.__class__.__name__, str(e))
        else:
            success = False
            self.cache.add_log_entry(self.__class__.__name__, f"No query provided.")

        return items, success
