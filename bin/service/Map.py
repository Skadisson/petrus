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

    def parse_comments(self, comments):
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
            normalized_ticket[field_name] = normalized_value
        normalized_ticket['Relevancy'] = relevancy_percentage
        normalized_ticket['Time_Spent'] = ticket['Time_Spent']
        if 'Organization' in ticket and ticket['Organization'] is not None:
            normalized_ticket['Organization'] = int(ticket['Organization'])
        else:
            normalized_ticket['Organization'] = -1
        return normalized_ticket
