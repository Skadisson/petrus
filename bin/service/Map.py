from bin.service import Environment
from bin.service import RegEx
from bin.service import Ranking
import json
import re
import time
import datetime


class Map:
    """Service Desk Ticket Mapper"""

    def __init__(self):
        self.environment = Environment.Environment()
        self.regex = RegEx.RegEx()
        self.ranking = Ranking.Ranking()

    def get_mapped_ticket(self, ticket_data_json):
        converted_data = {}
        ticket_data = json.loads(ticket_data_json)
        mapping = self.environment.get_map_ticket()
        for map_to_label in mapping:
            map_from_key = mapping[map_to_label]
            converted_data[map_to_label] = self.get_converted_value(map_from_key, ticket_data)
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

    def normalize_tickets(self, tickets):
        normalized_tickets = []
        for ticket in tickets:
            normalized_ticket = self.normalize_ticket(ticket)
            normalized_tickets.append(normalized_ticket)
        return normalized_tickets

    def normalize_ticket(self, ticket, relevancy_percentage=100.0):
        normalized_ticket = {}
        values = self.environment.get_map_values()
        keys = self.environment.get_map_keys()
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
        normalized_ticket['Rank'] = self.ranking.score_ticket(ticket)
        normalized_ticket['Relevancy'] = relevancy_percentage
        if ticket['Time_Spent'] is None:
            normalized_ticket['Time_Spent'] = 0
        else:
            normalized_ticket['Time_Spent'] = ticket['Time_Spent']
        if 'Organization' in ticket and ticket['Organization'] is not None:
            normalized_ticket['Organization'] = int(ticket['Organization'])
        else:
            normalized_ticket['Organization'] = -1
        if 'Status' in ticket and ticket['Status'] is not None:
            normalized_ticket['State_Changes'] = len(ticket['Status'])
        else:
            normalized_ticket['State_Changes'] = 0
        if 'Created' in ticket and ticket['Created'] is not None:
            normalized_ticket['Created'] = self.timestamp_from_ticket_time(ticket['Created'])
        else:
            normalized_ticket['Created'] = 0
        if 'Updated' in ticket and ticket['Updated'] is not None:
            normalized_ticket['Updated'] = self.timestamp_from_ticket_time(ticket['Updated'])
        else:
            normalized_ticket['Updated'] = 0
        if 'Closed' in ticket and ticket['Closed'] is not None:
            normalized_ticket['Closed'] = self.timestamp_from_ticket_time(ticket['Closed'])
        else:
            normalized_ticket['Closed'] = 0
        normalized_ticket['Key'] = 0
        if 'Key' in ticket and ticket['Key'] is not None:
            normalized_ticket['Key'] = 0
            for key in keys:
                if re.match(key, ticket['Key']):
                    normalized_ticket['Key'] = keys[key]

        return normalized_ticket

    @staticmethod
    def timestamp_from_ticket_time(ticket_time):
        if ticket_time is None:
            return 0
        return time.mktime(datetime.datetime.strptime(ticket_time, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    @staticmethod
    def format_status_history(mapped_ticket):
        if mapped_ticket['Status'] is not None:
            formatted_status_history = []
            for status in mapped_ticket['Status']['values']:
                millis = status['statusDate']['epochMillis']
                formatted_status_history.append({
                    'type': status['status'],
                    'milliseconds': millis
                })
                if 'LastProcessed' not in mapped_ticket or mapped_ticket['LastProcessed'] < millis:
                    mapped_ticket['LastProcessed'] = millis
            mapped_ticket['Status'] = formatted_status_history
        else:
            mapped_ticket['Status'] = []
        return mapped_ticket

    @staticmethod
    def format_worklog(mapped_ticket):
        persons = []
        if mapped_ticket['Worklog'] is not None:
            formatted_worklog = []
            if 'worklogs' in mapped_ticket['Worklog']:
                for worklog in mapped_ticket['Worklog']['worklogs']:
                    if worklog['author']['name'] not in persons:
                        persons.append(worklog['author']['name'])
                    formatted_worklog.append({
                        'updated': worklog['updated'],
                        'timeSpentSeconds': worklog['timeSpentSeconds']
                    })
                mapped_ticket['Worklog'] = formatted_worklog
        else:
            mapped_ticket['Worklog'] = []
        return mapped_ticket, persons

    @staticmethod
    def format_sla(mapped_ticket):
        formatted_sla = {}
        if mapped_ticket['SLA'] is not None:
            if 'ongoingCycle' in mapped_ticket['SLA']:
                formatted_sla = {
                    'start': mapped_ticket['SLA']['ongoingCycle']['startTime']['iso8601'],
                    'end': mapped_ticket['SLA']['ongoingCycle']['breachTime']['iso8601'],
                    'breached': mapped_ticket['SLA']['ongoingCycle']['breached']
                }
        mapped_ticket['SLA'] = formatted_sla
        return mapped_ticket

    def format_comments(self, mapped_ticket):
        persons = []
        if mapped_ticket['Comments'] is not None:
            formatted_comments = []
            if 'values' in mapped_ticket['Comments']:
                for comment in mapped_ticket['Comments']['values']:
                    if comment['body'] is not None:
                        comment_text = self.regex.mask_text(comment['body'])
                        formatted_comments.append(comment_text)
                    if comment['author']['name'] not in persons:
                        persons.append(comment['author']['name'])
                mapped_ticket['Comments'] = formatted_comments
        else:
            mapped_ticket['Comments'] = []
        return mapped_ticket, persons

    def format_text(self, mapped_ticket):
        if 'Text' in mapped_ticket and mapped_ticket['Text'] is not None:
            mapped_ticket['Text'] = self.regex.mask_text(mapped_ticket['Text'])
        return mapped_ticket

    @staticmethod
    def format_reporter(mapped_ticket):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if mapped_ticket['Reporter'] is not None and mapped_ticket['Reporter'] not in ['internal', 'external']:
            is_email = re.search(regex, mapped_ticket['Reporter'])
            if is_email:
                mapped_ticket['Reporter'] = 'external'
            else:
                mapped_ticket['Reporter'] = 'internal'
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

    @staticmethod
    def format_versions(mapped_ticket):
        formatted_versions = []
        for ticket_version in mapped_ticket['Versions']:
            if 'name' in ticket_version:
                formatted_versions.append(ticket_version['name'])
        mapped_ticket['Versions'] = formatted_versions
        return mapped_ticket

    @staticmethod
    def add_persons(mapped_ticket, persons):
        unique_persons = list(dict.fromkeys(persons))
        mapped_ticket['Persons'] = len(unique_persons)
        return mapped_ticket
