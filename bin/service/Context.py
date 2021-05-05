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

        suggested_keys = []
        sorted_relevancy = []
        keyword_total = len(keywords)
        if keyword_total != 0:
            phoenix_suggestion, suggested_keys = self.get_phoenix_ticket_suggestion(tickets, " ".join(keywords))
            if phoenix_suggestion is not None:
                sorted_relevancy.append(phoenix_suggestion)
        return sorted_relevancy, suggested_keys

    def add_to_relevancy(self, ticket, keywords, relevancy, relations):
        ticket_relevancy = self.calculate_ticket_relevancy(ticket, keywords, relations)
        if ticket_relevancy is not None and ticket_relevancy['percentage'] > 0:
            relevancy.append(ticket_relevancy)
        return relevancy

    def calculate_ticket_relevancy(self, ticket, keywords, relations):
        jira_id = ticket['ID']
        relevancy = None
        keyword_total = len(keywords)
        keyword_hits = []
        for keyword in ticket['Keywords']:
            if keyword in keywords:
                keyword_hits.append(keyword)
        hit_count = len(keyword_hits)
        if jira_id in relations:
            hit_count += 1
        if hit_count >= 2 and keyword_total > 0:
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

    def filter_similar_tickets(self, relevancy, jira_id):
        similar_tickets = []
        for rel_item in relevancy:
            rel_jira_id = str(rel_item['jira_id'])
            rel_percentage = rel_item['percentage']
            if rel_jira_id != jira_id:
                similar_ticket = self.cache.load_cached_ticket(rel_jira_id)
                if similar_ticket['Time_Spent'] is not None and similar_ticket['Time_Spent'] > 0:
                    normalized_similar_ticket = self.mapper.normalize_ticket(similar_ticket, rel_percentage)
                    similar_tickets.append(normalized_similar_ticket)
        hits = len(similar_tickets)

        return similar_tickets, hits

    def get_phoenix_ticket_suggestion(self, tickets, query):
        texts = []
        keys = []
        check_tickets = []
        suggested_keys = []
        suggested_ticket = None
        for ticket in tickets:
            check_tickets.append(ticket)
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
            if description is not None and key is not None and description != '':
                keys.append(key)
                texts.append(str(description))
        if len(texts) > 0:
            suggested_keys = self.scikit.get_phoenix_suggestion(texts, keys, query)
            for ticket in check_tickets:
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
                if key in suggested_keys:
                    suggested_ticket = {
                        'jira_id': ticket['ID'],
                        'percentage': 100,
                        'hits': [],
                        'link': self.environment.get_endpoint_ticket_link().format(key),
                        'project': ticket['Project'],
                        'creation': creation,
                        'time_spent': time_spent,
                        'title': title
                    }
        return suggested_ticket, suggested_keys
