from bin.service import Cache
import time
import datetime
from collections import Counter
import re


class Analyze:
    """Ticket and performance analytics"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.tickets = self.cache.load_cached_tickets()

    def ticket_count(self, for_days=30):
        ticket_count = 0
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if is_in_range is True:
                ticket_count += 1

        return ticket_count

    def hours_total(self, for_days=30):
        total = 0.0
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if is_in_range is True and ticket['Time_Spent'] is not None and ticket['Time_Spent'] > 0:
                total += ticket['Time_Spent'] / 60 / 60

        return total

    def hours_per_project(self, for_days=30):
        projects = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if is_in_range is True and 'Project' in ticket:
                if ticket['Project'] is not None:
                    if ticket['Project'] not in projects:
                        projects[ticket['Project']] = []
                    if ticket['Time_Spent'] is not None:
                        projects[ticket['Project']].append(ticket['Time_Spent'])

        projects = self.sort_tickets(projects)
        return projects

    def hours_per_type(self, for_days=30):
        types = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if is_in_range is True and 'Type' in ticket:
                if ticket['Type'] not in types:
                    types[ticket['Type']] = []
                if ticket['Time_Spent'] is not None:
                    types[ticket['Type']].append(ticket['Time_Spent'])

        types = self.sort_tickets(types)
        return types

    def hours_per_version(self, for_days=30):
        versions = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if is_in_range is True and 'Keywords' in ticket:
                version = None
                for keyword in ticket['Keywords']:
                    if re.match(r"bb[0-9.]", keyword):
                        version = keyword
                if version is not None:
                    if version not in versions:
                        versions[version] = []
                    if ticket['Time_Spent'] is not None:
                        versions[version].append(ticket['Time_Spent'])

        versions = self.sort_tickets(versions)
        return versions

    def hours_per_ticket(self, for_days=30):
        tickets = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            jira_key = self.cache.load_jira_key_for_id(jira_id)
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if jira_key is not None and is_in_range is True:
                if jira_key not in tickets:
                    tickets[jira_key] = []
                if ticket['Time_Spent'] is not None:
                    tickets[jira_key].append(ticket['Time_Spent'])

        tickets = self.sort_tickets(tickets)
        return tickets

    def problematic_tickets(self, for_days=30):
        problematic_tickets = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if is_in_range is True:
                problematic_tickets = self.add_to_problematic_tickets(ticket, problematic_tickets)

        problematic_tickets = self.sort_tickets(problematic_tickets)
        return problematic_tickets

    def add_to_problematic_tickets(self, ticket, problematic_tickets):
        jira_key = self.cache.load_jira_key_for_id(ticket['ID'])
        if jira_key is None or ticket['Time_Spent'] is None:
            return problematic_tickets

        if jira_key not in problematic_tickets:
            problematic_tickets[jira_key] = []
        is_above_four_hours = ticket['Time_Spent'] > 14400
        got_changed_over_four_times = 'State_Changes' in ticket and ticket['State_Changes'] > 4
        has_sufficient_data = is_above_four_hours or got_changed_over_four_times
        if has_sufficient_data:
            problematic_tickets[jira_key].append(ticket['Time_Spent'])

        return problematic_tickets

    @staticmethod
    def sort_tickets(seconds_spent_per_attribute):
        accumulated_hours_spent = {}
        for attribute in seconds_spent_per_attribute:
            accumulated_hours_spent[attribute] = 0
            seconds_spent = seconds_spent_per_attribute[attribute]
            for seconds in seconds_spent:
                hours = seconds / 60 / 60
                accumulated_hours_spent[attribute] += round(hours, 2)
        top_tickets = [
            (k, accumulated_hours_spent[k]) for k in sorted(accumulated_hours_spent,
                                                            key=accumulated_hours_spent.get,
                                                            reverse=True)
        ]
        return top_tickets

    def ticket_is_in_range(self, ticket, for_days=30):
        if 'LastProcessed' not in ticket:
            time_updated = self.timestamp_from_ticket_time(ticket['Updated'])
        else:
            time_updated = int(ticket['LastProcessed']) / 1000
        current_time_stamp = datetime.datetime.now().timestamp()
        max_gap = for_days * 24 * 60 * 60
        return time_updated >= (current_time_stamp - max_gap)

    @staticmethod
    def timestamp_from_ticket_time(ticket_time):
        return time.mktime(datetime.datetime.strptime(ticket_time, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    def word_count_and_relations(self):
        words = []
        word_relations = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            for keyword in ticket['Keywords']:
                words.append(keyword)
                if keyword not in word_relations:
                    word_relations[keyword] = []
                for related_keyword in ticket['Keywords']:
                    if related_keyword is not keyword:
                        word_relations[keyword].append(related_keyword)
        word_count = Counter(words)
        return word_count, word_relations
