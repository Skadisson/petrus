from bin.service import Environment
import json


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
        return converted_data

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
