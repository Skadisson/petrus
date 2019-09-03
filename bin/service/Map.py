from bin.service import Environment
import json
from collections import Counter


class Map:
    """Service Desk Ticket Mapper"""

    def __init__(self):
        self.environment = Environment.Environment()

    def get_mapped_ticket(self, ticket_data_json):
        converted_data = {}
        ticket_data = json.loads(ticket_data_json)
        mapping = self.environment.get_map_ticket()
        for map_to_label in mapping:
            map_from_key = mapping[map_to_label]
            converted_data[map_to_label] = self.get_converted_value(map_from_key, ticket_data)
        converted_data['Comments'] = Counter(self.parse_comments(converted_data['Comments']))
        return converted_data

    @staticmethod
    def parse_comments(comments):
        parsed_comments_words = []
        for comment in comments:
            parsed_words = comment['body'].split()
            for parsed_word in parsed_words:
                parsed_comments_words.append(parsed_word)
        return parsed_comments_words

    def get_converted_value(self, key, ticket_data):
        key_is_string = isinstance(key, str)
        if isinstance(ticket_data, list) and len(ticket_data) > 0:
            ticket_data = ticket_data[0]
        if ticket_data is not None and key_is_string and key in ticket_data:
            data = ticket_data[key]
            return data
        elif ticket_data is not None:
            for map_from_key in key:
                if map_from_key in ticket_data:
                    data = ticket_data[map_from_key]
                    return self.get_converted_value(key[map_from_key], data)
        return None

    def normalize_ticket(self, ticket, relevancy_percentage=100.0):
        normalized_ticket = {}
        values = self.environment.get_map_values()
        for field_name in values:
            if field_name in ticket:
                actual_value = ticket[field_name]
            else:
                actual_value = -1
            if actual_value in values[field_name]:
                normalized_value = values[field_name][actual_value]
            else:
                normalized_value = -1
            if normalized_value is None:
                normalized_value = -1
            normalized_ticket[field_name] = normalized_value
        normalized_ticket['Relevancy'] = relevancy_percentage
        if ticket['Time_Spent'] is None:
            normalized_ticket['Time_Spent'] = 0
        else:
            normalized_ticket['Time_Spent'] = ticket['Time_Spent']
        if 'Organization' in ticket and ticket['Organization'] is not None:
            normalized_ticket['Organization'] = int(ticket['Organization'])
        else:
            normalized_ticket['Organization'] = -1
        if 'Comments' in ticket and ticket['Comments'] is not None:
            normalized_ticket['Words'] = sum(ticket['Comments'].values())
        else:
            normalized_ticket['Words'] = 0
        if 'Status' in ticket and ticket['Status'] is not None:
            normalized_ticket['State_Changes'] = len(ticket['Status'])
        else:
            normalized_ticket['State_Changes'] = 0
        return normalized_ticket

    @staticmethod
    def format_status_history(mapped_ticket):
        if mapped_ticket['Status'] is not None:
            formatted_status_history = []
            for status in mapped_ticket['Status']['values']:
                formatted_status_history.append({
                    'type': status['status'],
                    'milliseconds': status['statusDate']['epochMillis']
                })
            mapped_ticket['Status'] = formatted_status_history
        else:
            mapped_ticket['Status'] = []
        return mapped_ticket

    def format_related_tickets(self, mapped_ticket):
        formatted_related_tickets = []
        allowed_relations = self.environment.get_map_relation()
        for ticket_relation in mapped_ticket['Related']:
            if 'inwardIssue' in ticket_relation:
                if ticket_relation['type']['inward'] in allowed_relations:
                    formatted_related_tickets.append(str(ticket_relation['inwardIssue']['id']))
            if 'outwardIssue' in ticket_relation:
                if ticket_relation['type']['outward'] in allowed_relations:
                    formatted_related_tickets.append(str(ticket_relation['outwardIssue']['id']))
        mapped_ticket['Related'] = formatted_related_tickets
        return mapped_ticket
