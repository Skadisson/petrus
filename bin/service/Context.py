from bin.service import Environment
from bin.service import Map
from bin.service import Cache
from bin.service import SciKitLearn
import time, datetime, sys


class Context:
    """Context Calculator"""

    def __init__(self):
        self.environment = Environment.Environment()
        self.mapper = Map.Map()
        self.cache = Cache.Cache()
        self.scikit = SciKitLearn.SciKitLearn()

    def calculate_relevancy_for_tickets(self, tickets, mapped_ticket):
        keywords = mapped_ticket['Keywords']
        relations = mapped_ticket['Related']

        sorted_relevancy = []
        relevancy = []
        keyword_total = len(keywords)
        if keyword_total != 0:
            for jira_id in tickets:
                relevancy = self.add_to_relevancy(tickets, jira_id, keywords, relevancy, relations)
            sorted_relevancy = self.sort_relevancy(relevancy)
            if len(sorted_relevancy) == 0:
                phoenix_suggestion = self.get_phoenix_ticket_suggestion(tickets, " ".join(keywords))
                if phoenix_suggestion is not None:
                    sorted_relevancy.append(phoenix_suggestion)
        return sorted_relevancy

    def add_relevancy_for_commits(self, commits, keywords, relevancy):
        phoenix_suggestion = self.get_phoenix_commit_suggestion(commits, " ".join(keywords))
        if phoenix_suggestion is not None:
            relevancy.append(phoenix_suggestion)
        return relevancy
    
    def add_relevancy_for_documents(self, documents, keywords, relevancy):
        phoenix_suggestion = self.get_phoenix_document_suggestion(documents, " ".join(keywords))
        if phoenix_suggestion is not None:
            relevancy.append(phoenix_suggestion)
        return relevancy

    def add_to_relevancy(self, tickets, jira_id, keywords, relevancy, relations):
        ticket_data = tickets[str(jira_id)]
        ticket_relevancy = self.calculate_ticket_relevancy(ticket_data, keywords, jira_id, relations)
        if ticket_relevancy is not None and ticket_relevancy['percentage'] > 0:
            relevancy.append(ticket_relevancy)
        return relevancy

    def calculate_ticket_relevancy(self, ticket, keywords, jira_id, relations):
        relevancy = None
        keyword_total = len(keywords)
        keyword_hits = []
        for keyword in ticket['Keywords']:
            if keyword in keywords:
                keyword_hits.append(keyword)
        hit_count = len(keyword_hits)
        if jira_id in relations:
            hit_count += 1
        if hit_count >= 2:
            percentage = hit_count / keyword_total * 100
            jira_key = self.cache.load_jira_key_for_id(jira_id)
            ticket_link = self.environment.get_endpoint_ticket_link().format(jira_key)
            ticket_organization = str(ticket['Project'])
            creation = self.timestamp_from_ticket_time(ticket['Created'])
            if ticket['Time_Spent'] is not None:
                time_spent = self.seconds_to_hours(int(ticket['Time_Spent']))
            else:
                time_spent = 0
            if percentage > 0:
                relevancy = {
                    "jira_id": str(jira_id),
                    "percentage": percentage,
                    "hits": keyword_hits,
                    "link": ticket_link,
                    "project": ticket_organization,
                    "creation": creation,
                    "time_spent": time_spent
                }
                if 'Title' in ticket:
                    relevancy['title'] = ticket['Title']

        return relevancy

    @staticmethod
    def timestamp_from_ticket_time(ticket_time):
        if ticket_time is None:
            return 0
        return time.mktime(datetime.datetime.strptime(ticket_time, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    @staticmethod
    def seconds_to_hours(seconds):
        return seconds / 60 / 60

    @staticmethod
    def sort_relevancy(relevancy):
        def get_key(item):
            return item['percentage']
        return sorted(relevancy, key=get_key, reverse=True)

    def filter_similar_tickets(self, relevancy, cached_tickets, jira_id):
        similar_tickets = []
        for rel_item in relevancy:
            rel_jira_id = str(rel_item['jira_id'])
            rel_percentage = rel_item['percentage']
            if rel_jira_id != jira_id and rel_jira_id in cached_tickets:
                similar_ticket = cached_tickets[rel_jira_id]
                if similar_ticket['Time_Spent'] is not None and similar_ticket['Time_Spent'] > 0:
                    normalized_similar_ticket = self.mapper.normalize_ticket(similar_ticket, rel_percentage)
                    similar_tickets.append(normalized_similar_ticket)
        hits = len(similar_tickets)

        return similar_tickets, hits

    def get_phoenix_ticket_suggestion(self, tickets, query):
        texts = []
        keys = []
        suggested_ticket = None
        for ticket_id in tickets:
            ticket = tickets[ticket_id]
            title = str(ticket['Title'])
            description = str(ticket['Text'])
            description += " || " + str(title)
            comments = ticket['Comments']
            if comments is not None:
                description += " || " + (" || ".join(comments))
            keywords = ticket['Keywords']
            if keywords is not None:
                description += " || " + (", ".join(keywords))
            project = ticket['Project']
            if project is not None:
                description += " || " + project
            key = ticket['Key']
            if description is not None and key is not None:
                keys.append(key)
                texts.append(str(description))
        suggested_key = self.scikit.get_phoenix_suggestion(texts, keys, query)
        for ticket_id in tickets:
            ticket = tickets[ticket_id]
            key = ticket['Key']
            creation = self.timestamp_from_ticket_time(ticket['Created'])
            if ticket['Time_Spent'] is not None:
                time_spent = self.seconds_to_hours(int(ticket['Time_Spent']))
            else:
                time_spent = 0
            if 'Title' in ticket:
                title = ticket['Title']
            else:
                title = ''
            if suggested_key == key:
                suggested_ticket = {
                    'jira_id': ticket_id,
                    'percentage': 100,
                    'hits': [],
                    'link': self.environment.get_endpoint_ticket_link().format(key),
                    'project': ticket['Project'],
                    'creation': creation,
                    'time_spent': time_spent,
                    'title': title
                }
        return suggested_ticket

    def get_phoenix_commit_suggestion(self, commits, query):
        private_token = self.environment.get_endpoint_git_private_token()
        texts = []
        keys = []
        suggested_commit = None
        for git_hash in commits:
            commit = commits[git_hash]
            if commit['title'] != '' and commit['text'] != '':
                text = commit['title'] + ' ' + commit['text']
                texts.append(text)
                keys.append(git_hash)
                gigs_used = sys.getsizeof(texts)/1024/1024
                if gigs_used >= 0.2:
                    break
        suggested_key = self.scikit.get_phoenix_suggestion(texts, keys, query)
        if suggested_key in commits:
            commit = commits[suggested_key]
            suggested_commit = {
                'jira_id': suggested_key,
                'percentage': 100,
                'hits': [],
                'link': self.environment.get_endpoint_git_link().format(commit['project'], suggested_key, private_token),
                'project': None,
                'creation': None,
                'time_spent': None,
                'title': commit['title']
            }

        return suggested_commit

    def get_phoenix_document_suggestion(self, documents, query):
        texts = []
        keys = []
        suggested_document = None
        for confluence_id in documents:
            document = documents[confluence_id]
            text = document['title'] + ' ' + document['text']
            texts.append(text)
            keys.append(confluence_id)
        suggested_id = self.scikit.get_phoenix_suggestion(texts, keys, query)
        if suggested_id in documents:
            document = documents[suggested_id]
            suggested_document = {
                'jira_id': suggested_id,
                'percentage': 100,
                'hits': [],
                'link': document['link'],
                'project': document['project'],
                'creation': None,
                'time_spent': None,
                'title': document['title']
            }

        return suggested_document
