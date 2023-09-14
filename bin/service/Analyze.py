from bin.service import Cache
from bin.service import Context
from bin.service import Map
from bin.service import Environment
from bin.service import Ranking
import time
import datetime
from collections import Counter
import collections
import re
import numpy
import math


class Analyze:
    """Ticket and performance analytics"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.context = Context.Context()
        self.mapper = Map.Map()
        self.environment = Environment.Environment()
        self.ranking = Ranking.Ranking()
        self.filtered_tickets = None
        self.in_range = {}

    def ticket_count(self, tickets):
        ticket_count = 0
        external_count = 0
        internal_count = 0
        for ticket in tickets:
            ticket_count += 1
            if 'Reporter' in ticket:
                if ticket['Reporter'] == 'internal':
                    internal_count += 1
                else:
                    external_count += 1

        return ticket_count, internal_count, external_count

    def get_yer_tickets(self):
        if self.filtered_tickets is None:
            tickets = self.cache.load_cached_tickets()
            self.filtered_tickets = self.filter_dates_of_horror(tickets)
        return self.filtered_tickets

    def filter_tickets_for_range(self, tickets, days, year, week_numbers, start):
        filtered_tickets = []
        for ticket in tickets:
            in_range = self.ticket_is_in_range(ticket, days, year, week_numbers, start)
            if in_range:
                filtered_tickets.append(ticket)
        return filtered_tickets

    def top_and_bottom_tickets(self, tickets, top_count=5):
        ranked_tickets = []
        for ticket in tickets:
            concluded = len(ticket['Status']) > 0 and 'type' in ticket['Status'][0] and ticket['Status'][0]['type'] == 'Fertig'
            actually_needed_effort = 'Time_Spent' in ticket and ticket['Time_Spent'] is not None and ticket['Time_Spent'] > 0
            if actually_needed_effort is True and concluded is True:
                ranked_ticket = ticket
                ranked_ticket['Rank'] = self.score_ticket(ticket)
                ranked_tickets.append(ranked_ticket)

        sorted_ranked_tickets = sorted(ranked_tickets, key=lambda ticket: ticket['Rank'], reverse=True)
        top_tickets = sorted_ranked_tickets[:top_count]
        bottom_tickets = sorted_ranked_tickets[-top_count:]

        top_ticket_ranks = {}
        for top_ticket in top_tickets:
            if 'Key' in top_ticket and 'Rank' in top_ticket:
                top_ticket_ranks[top_ticket['Key']] = top_ticket['Rank']

        bottom_ticket_ranks = {}
        for bottom_ticket in bottom_tickets:
            if 'Key' in bottom_ticket and 'Rank' in bottom_ticket:
                bottom_ticket_ranks[bottom_ticket['Key']] = bottom_ticket['Rank']

        return top_ticket_ranks, bottom_ticket_ranks

    def hours_total(self, tickets):
        total = 0.0
        for ticket in tickets:
            if ticket['Time_Spent'] is not None and ticket['Time_Spent'] > 0:
                total += ticket['Time_Spent'] / 60 / 60

        return total

    def hours_per_project(self, tickets):
        projects = {}
        ticket_count = {}
        for ticket in tickets:
            project_name = ticket['Project']
            if project_name is not None:
                if project_name not in projects:
                    projects[project_name] = []
                if project_name not in ticket_count:
                    ticket_count[project_name] = 0
                if ticket['Time_Spent'] is not None:
                    projects[project_name].append(ticket['Time_Spent'])
                    ticket_count[project_name] += 1

        projects = self.sort_tickets_and_seconds_to_hours(projects)
        return projects, ticket_count

    def payed_unpayed(self, tickets):
        payed_unpayed = {
            'payed': {
                'value': 0.0,
                'label': 'potenziell abrechenbar'
            },
            'unpayed': {
                'value': 0.0,
                'label': 'nicht abrechenbar'
            }
        }
        for ticket in tickets:
            if 'Time_Spent' in ticket and ticket['Time_Spent'] is not None and 'CostLocation' in ticket and ticket['CostLocation'] is not None and 'id' in ticket['CostLocation']:
                hours = ticket['Time_Spent'] / 60 / 60
                if int(ticket['CostLocation']['id']) in [10500, 11200, 10402]:
                    payed_unpayed['payed']['value'] += hours
                else:
                    payed_unpayed['unpayed']['value'] += hours

        total = payed_unpayed['payed']['value'] + payed_unpayed['unpayed']['value']
        payed_unpayed['payed']['label'] = f"{math.floor(payed_unpayed['payed']['value'])}h {payed_unpayed['payed']['label']} ({math.floor(payed_unpayed['payed']['value'] / total * 100)} %)"
        payed_unpayed['unpayed']['label'] = f"{math.floor(payed_unpayed['unpayed']['value'])}h {payed_unpayed['unpayed']['label']} ({math.floor(payed_unpayed['unpayed']['value'] / total * 100)} %)"

        return payed_unpayed

    def hours_per_system(self, tickets):

        domain_regex = r'^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)'

        domains = {}
        ticket_count = {}
        system_versions = {}
        for ticket in tickets:
            if 'System' in ticket:
                system_url = ticket['System']
                project_name = ticket['Project']
                if system_url is not None and system_url != '':
                    domain_reg = re.compile(domain_regex)
                    domain_matches = domain_reg.search(system_url)
                    domain = domain_matches[1]
                    if domain is not None:
                        if project_name not in domains:
                            domains[project_name] = {}
                        if domain not in domains[project_name]:
                            domains[project_name][domain] = []
                        if project_name not in ticket_count:
                            ticket_count[project_name] = {}
                        if domain not in ticket_count[project_name]:
                            ticket_count[project_name][domain] = 0
                        if ticket['Time_Spent'] is not None and ticket['Time_Spent'] >= 0.0:
                            domains[project_name][domain].append(round(float(ticket['Time_Spent']) / 60 / 60, 2))
                            ticket_count[project_name][domain] += 1
                        version = None
                        for keyword in ticket['Keywords']:
                            if re.match(r"bb[0-9.]", keyword):
                                version = keyword
                        if version is not None:
                            if project_name not in system_versions:
                                system_versions[project_name] = {}
                            if domain not in system_versions[project_name]:
                                system_versions[project_name][domain] = []
                            if version not in system_versions[project_name][domain]:
                                system_versions[project_name][domain].append(version)

        return domains, ticket_count, system_versions

    def hours_per_type(self, tickets):
        types = {}
        for ticket in tickets:
            if 'Type' in ticket:
                if ticket['Type'] not in types:
                    types[ticket['Type']] = []
                if ticket['Time_Spent'] is not None:
                    types[ticket['Type']].append(ticket['Time_Spent'])

        types = self.sort_tickets_and_seconds_to_hours(types)
        return types

    def hours_per_version(self, tickets):
        versions = {}
        projects = {}
        for ticket in tickets:
            if 'Keywords' in ticket:
                version = None
                for keyword in ticket['Keywords']:
                    if re.match(r"bb[0-9.]", keyword):
                        version = keyword
                if version is not None:
                    if version not in versions:
                        versions[version] = []
                    if version not in projects:
                        projects[version] = []
                    if ticket['Time_Spent'] is not None:
                        versions[version].append(ticket['Time_Spent'])
                        if ticket['Project'] is not None and ticket['Project'] not in projects[version]:
                            projects[version].append(ticket['Project'])

        versions = self.sort_tickets_and_seconds_to_hours(versions)
        return versions, projects

    def hours_per_ticket(self, stored_tickets):
        tickets = {}
        for ticket in stored_tickets:
            jira_key = self.cache.load_jira_key_for_id(ticket['ID'])
            if jira_key is not None:
                if jira_key not in tickets:
                    tickets[jira_key] = []
                if ticket['Time_Spent'] is not None:
                    tickets[jira_key].append(ticket['Time_Spent'])

        tickets = self.sort_tickets_and_seconds_to_hours(tickets)
        return tickets

    def lifetime_per_ticket(self, stored_tickets):
        tickets = {}
        for ticket in stored_tickets:
            if 'Versions' in ticket and len(ticket['Versions']) > 0:
                continue
            jira_key = self.cache.load_jira_key_for_id(ticket['ID'])
            if jira_key is not None:
                if len(ticket['Status']) > 0 and 'type' in ticket['Status'][0] and ticket['Status'][0]['type'] in ["Fertig"] \
                        and ticket['Created'] is not None and ticket['Closed'] is not None:
                    time_created = self.timestamp_from_ticket_time(ticket['Created'])
                    time_closed = self.timestamp_from_ticket_time(ticket['Closed'])
                    if 0 < time_created < time_closed and time_closed > 0:
                        diff = time_closed - time_created
                        if jira_key not in tickets:
                            tickets[jira_key] = []
                        tickets[jira_key].append(diff)

        tickets = self.sort_tickets_and_seconds_to_hours(tickets)
        return tickets

    def load_tickets_for_days(self, for_days=0):
        tickets = []
        stored_tickets = self.get_yer_tickets()
        for ticket in stored_tickets:
            jira_key = self.cache.load_jira_key_for_id(ticket['ID'])
            is_in_range = self.ticket_is_in_range(ticket, for_days)
            if jira_key is not None and is_in_range is True:
                tickets.append(ticket)

        return tickets

    @staticmethod
    def seconds_to_hours(seconds):
        return seconds / 60 / 60

    def plot_data(self, tickets):
        relevant_tickets = []
        for ticket in tickets:
            ticket = self.mapper.normalize_ticket(ticket)
            relevant_tickets.append(ticket)

        new_tickets_per_day = {}
        for ticket in relevant_tickets:
            if ticket['Created'] != '' and ticket['Created'] != 0:
                date = int(datetime.datetime.fromtimestamp(ticket['Created']).strftime("%Y%m%d"))
                if date in new_tickets_per_day:
                    new_tickets_per_day[date] += 1
                else:
                    new_tickets_per_day[date] = 1
            if ticket['Closed'] != '' and ticket['Closed'] != 0:
                date = int(datetime.datetime.fromtimestamp(ticket['Closed']).strftime("%Y%m%d"))
                if date in new_tickets_per_day:
                    new_tickets_per_day[date] -= 1
                else:
                    new_tickets_per_day[date] = -1

        wait_per_priority = {}
        for ticket in relevant_tickets:
            priority = ticket['Priority']
            if 'Versions' in ticket and len(ticket['Versions']) > 0:
                continue
            if priority not in wait_per_priority:
                wait_per_priority[priority] = []
            if ticket['Created'] > 0 and ticket['Closed'] > 0:
                days = (ticket['Closed'] - ticket['Created']) / 60 / 60 / 24
                if ticket['Time_Spent'] is not None and ticket['Time_Spent'] > 0:
                    wait_per_priority[priority].append(days)
        time_per_priority = {}
        for priority in wait_per_priority:
            if len(wait_per_priority[priority]) > 0:
                time_per_priority[priority] = numpy.average(wait_per_priority[priority])

        plot_data = {
            "new tickets/day": collections.OrderedDict(sorted(new_tickets_per_day.items())),
            "average days/priority": collections.OrderedDict(sorted(time_per_priority.items()))
        }

        return plot_data

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
    def sort_tickets_and_seconds_to_hours(seconds_spent_per_attribute):
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

    def ticket_is_in_range(self, ticket, for_days=0, year="", week_numbers="", start=0):
        if ticket['ID'] in self.in_range:
            return self.in_range[ticket['ID']]
        is_in_range = False
        time_updated = self.timestamp_from_ticket_time(ticket['Created'])
        current_time_stamp = datetime.datetime.now().timestamp()
        if start > 0:
            current_time_stamp += (start * for_days * 24 * 60 * 60)
        if for_days > 0:
            max_gap = for_days * 24 * 60 * 60
            is_in_range = current_time_stamp >= time_updated >= (current_time_stamp - max_gap)
            if is_in_range and year != "":
                ticket_year = str(datetime.datetime.fromtimestamp(time_updated).strftime("%Y"))
                is_in_range = ticket_year == year
        elif week_numbers != "":
            weeks = week_numbers.split(',')
            ticket_week_number = str(int(datetime.datetime.fromtimestamp(time_updated).strftime("%W")) + 1)
            ticket_year = str(datetime.datetime.fromtimestamp(time_updated).strftime("%Y"))
            if year != "":
                is_in_range = year == ticket_year and ticket_week_number in weeks
            else:
                is_in_range = ticket_week_number in weeks
        elif year != "":
            ticket_year = datetime.datetime.fromtimestamp(time_updated).strftime("%Y")
            is_in_range = year == ticket_year

        self.in_range[ticket['ID']] = is_in_range
        return is_in_range

    @staticmethod
    def timestamp_from_ticket_time(ticket_time):
        if ticket_time is None:
            return 0
        return time.mktime(datetime.datetime.strptime(ticket_time, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    def word_count_and_relations(self):
        words = []
        word_relations = {}
        tickets = self.get_yer_tickets()
        for ticket in tickets:
            for keyword in ticket['Keywords']:
                words.append(keyword)
                if keyword not in word_relations:
                    word_relations[keyword] = []
                for related_keyword in ticket['Keywords']:
                    if related_keyword is not keyword:
                        word_relations[keyword].append(related_keyword)
        word_count = Counter(words)
        return word_count, word_relations

    def get_calendar_week(self, time):
        time_updated = self.timestamp_from_ticket_time(time)
        date_uploaded = datetime.datetime.fromtimestamp(time_updated)
        calendar_week = date_uploaded.strftime("%V")
        return calendar_week

    def get_calendar_year(self, time):
        time_updated = self.timestamp_from_ticket_time(time)
        date_uploaded = datetime.datetime.fromtimestamp(time_updated)
        calendar_year = date_uploaded.strftime("%Y")
        return calendar_year

    def ticket_opened_calendar(self, tickets):
        return self.ticket_calendar(tickets, 'Created')

    def ticket_closed_calendar(self, tickets):
        return self.ticket_calendar(tickets, 'Closed')

    def ticket_effort_calendar(self, tickets):
        ticket_effort_calendar = {}
        labels = []
        categories = self.environment.get_map_categories()
        for ticket in tickets:
            if 'Worklog' not in ticket or ticket['Worklog'] is None:
                continue
            for worklog in ticket['Worklog']:
                calendar_week = self.get_calendar_week(worklog['updated'])
                year = self.get_calendar_year(worklog['updated'])
                if year and calendar_week:
                    label = year + '.' + calendar_week
                    if label not in labels:
                        labels.append(label)
                    if worklog['timeSpentSeconds'] is not None:
                        ticket_type = ticket['Type']
                        for category in categories:
                            if ticket_type in categories[category]:
                                ticket_type = category
                                break
                        if year and calendar_week and ticket_type:
                            label = year + '.' + calendar_week
                            if label not in labels:
                                labels.append(label)
                            if label not in ticket_effort_calendar:
                                ticket_effort_calendar[label] = {}
                            if ticket_type not in ticket_effort_calendar[label]:
                                ticket_effort_calendar[label][ticket_type] = 0
                            ticket_effort_calendar[label][ticket_type] += self.seconds_to_hours(int(worklog['timeSpentSeconds']))
        ordered_labels = sorted(labels)
        ordered_effort_calendar = {}
        for label in ordered_labels:
            ordered_effort_calendar[label] = ticket_effort_calendar[label]
        return ordered_effort_calendar

    def ticket_calendar(self, tickets, state='Created'):
        ticket_opened_calendar = {}
        labels = []
        categories = self.environment.get_map_categories()
        for ticket in tickets:
            if state not in ticket:
                continue
            calendar_week = self.get_calendar_week(ticket[state])
            year = self.get_calendar_year(ticket[state])
            ticket_type = ticket['Type']
            for category in categories:
                if ticket_type in categories[category]:
                    ticket_type = category
                    break
            if year and calendar_week and ticket_type:
                label = year + '.' + calendar_week
                if label not in labels:
                    labels.append(label)
                if label not in ticket_opened_calendar:
                    ticket_opened_calendar[label] = {}
                if ticket_type not in ticket_opened_calendar[label]:
                    ticket_opened_calendar[label][ticket_type] = 0
                ticket_opened_calendar[label][ticket_type] += 1
        ordered_labels = sorted(labels)
        ordered_opened_calendar = {}
        for label in ordered_labels:
            ordered_opened_calendar[label] = ticket_opened_calendar[label]
        return ordered_opened_calendar

    def score_labeled_tickets(self, labeled_tickets):
        scores = {}
        for label in labeled_tickets:
            ranked_tickets = self.rank_tickets(labeled_tickets[label])
            scores[label] = numpy.average(numpy.array(list(ranked_tickets.values())).astype(int))
        top_scores = [
            (k, scores[k]) for k in sorted(scores, key=scores.get, reverse=True)
        ]
        return top_scores

    def rank_tickets(self, tickets):
        ticket_ranks = {}
        for ticket_id in tickets:
            ticket_ranks[ticket_id] = self.rank_ticket(tickets[ticket_id])
        return ticket_ranks

    def rank_ticket(self, ticket):
        return self.score_ticket(ticket)

    def score_ticket(self, ticket):
        return self.ranking.score_ticket(ticket)

    def score_tickets(self, tickets):
        total_score = 0
        for ticket in tickets:
            total_score += self.score_ticket(ticket)

        return total_score

    def normalize_ticket_for_ranks(self, ticket):
        closed_count = 0
        if 'Status' in ticket:
            for state in ticket['Status']:
                if state['type'] in ['Final abgeschlossen', 'Fertig', 'Done', 'Schliessen', 'Schließen', 'Closed', 'Gelöst']:
                    closed_count += 1
        breached = False
        if 'SLA' in ticket and ticket['SLA'] is not None and 'breached' in ticket['SLA'] and ticket['SLA']['breached'] is not None:
            breached = ticket['SLA']['breached']
        support = False
        if ticket['Type'] is not None and ticket['Type'] in ['Hilfe / Support', 'Neue Funktion', 'Anfrage', 'Änderung', 'Story', 'Epic', 'Serviceanfrage', 'Aufgabe', 'Media Service', 'Information']:
            support = True
        persons = 0
        if 'Persons' in ticket and ticket['Persons'] is not None:
            persons = int(ticket['Persons'])
        normalized_ticket = {
            'comments': len(ticket['Comments']),
            'breached': int(breached),
            'persons': persons,
            'relations': len(ticket['Related']),
            'closed': closed_count,
            'support': int(support)
        }
        return normalized_ticket

    def filter_dates_of_horror(self, _tickets):
        filtered_tickets = []
        dates_of_horror = self.environment.get_map_dates_of_horror()
        for ticket in _tickets:
            if "Created" in ticket and ticket["Created"] is not None:
                ticket_date = self.get_year_month_day(ticket['Created'])
                if ticket_date not in dates_of_horror:
                    filtered_tickets.append(ticket)

        return filtered_tickets

    def get_year_month_day(self, _timestamp):
        return datetime.datetime.fromtimestamp(self.timestamp_from_ticket_time(_timestamp)).strftime("%Y/%m/%d")
