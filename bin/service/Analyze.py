from bin.service import Cache
from bin.service import SciKitLearn
from bin.service import Context
from bin.service import Map
from bin.service import Environment
import time
import datetime
from collections import Counter
import re


class Analyze:
    """Ticket and performance analytics"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.tickets = self.cache.load_cached_tickets()
        self.sci_kit = SciKitLearn.SciKitLearn()
        self.context = Context.Context()
        self.mapper = Map.Map()
        self.environment = Environment.Environment()

    def ticket_count(self, for_days=0, year="", week_numbers=""):
        ticket_count = 0
        external_count = 0
        internal_count = 0
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
            if is_in_range is True:
                ticket_count += 1
                if 'Reporter' in ticket:
                    if ticket['Reporter'] == 'internal':
                        internal_count += 1
                    else:
                        external_count += 1

        return ticket_count, internal_count, external_count

    def hours_total(self, for_days=0, year="", week_numbers=""):
        total = 0.0
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
            if is_in_range is True and ticket['Time_Spent'] is not None and ticket['Time_Spent'] > 0:
                total += ticket['Time_Spent'] / 60 / 60

        return total

    def hours_per_project(self, for_days=0, year="", week_numbers=""):
        projects = {}
        ticket_count = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
            if is_in_range is True and 'Project' in ticket:
                project_name = ticket['Project']
                if project_name is not None:
                    if project_name not in projects:
                        projects[project_name] = []
                    if project_name not in ticket_count:
                        ticket_count[project_name] = 0
                    if ticket['Time_Spent'] is not None:
                        projects[project_name].append(ticket['Time_Spent'])
                        ticket_count[project_name] += 1

        projects = self.sort_tickets(projects)
        return projects, ticket_count

    def hours_per_system(self, for_days=0, year="", week_numbers=""):

        domain_regex = r'^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)'

        domains = {}
        ticket_count = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
            if is_in_range is True and 'System' in ticket:
                system_url = ticket['System']
                if system_url is not None and system_url != '':
                    domain_reg = re.compile(domain_regex)
                    domain_matches = domain_reg.search(system_url)
                    domain = domain_matches[1]
                    if domain is not None:
                        if domain not in domains:
                            domains[domain] = []
                        if domain not in ticket_count:
                            ticket_count[domain] = 0
                        if ticket['Time_Spent'] is not None:
                            domains[domain].append(ticket['Time_Spent'])
                            ticket_count[domain] += 1

        systems = self.sort_tickets(domains)
        return systems, ticket_count

    def hours_per_type(self, for_days=0, year="", week_numbers=""):
        types = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
            if is_in_range is True and 'Type' in ticket:
                if ticket['Type'] not in types:
                    types[ticket['Type']] = []
                if ticket['Time_Spent'] is not None:
                    types[ticket['Type']].append(ticket['Time_Spent'])

        types = self.sort_tickets(types)
        return types

    def hours_per_version(self, for_days=0, year="", week_numbers=""):
        versions = {}
        projects = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
            if is_in_range is True and 'Keywords' in ticket:
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

        versions = self.sort_tickets(versions)
        return versions, projects

    def hours_per_ticket(self, for_days=0, year="", week_numbers=""):
        tickets = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            jira_key = self.cache.load_jira_key_for_id(jira_id)
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
            if jira_key is not None and is_in_range is True:
                if jira_key not in tickets:
                    tickets[jira_key] = []
                if ticket['Time_Spent'] is not None:
                    tickets[jira_key].append(ticket['Time_Spent'])

        tickets = self.sort_tickets(tickets)
        return tickets

    @staticmethod
    def seconds_to_hours(seconds):
        return seconds / 60 / 60

    def format_tickets(self, mapped_ticket):
        cached_tickets = self.cache.load_cached_tickets()
        relevancy = self.context.calculate_relevancy_for_tickets(cached_tickets, mapped_ticket)
        normalized_ticket = self.mapper.normalize_ticket(mapped_ticket)
        similar_tickets, hits = self.context.filter_similar_tickets(
            relevancy,
            cached_tickets,
            mapped_ticket['ID']
        )
        return normalized_ticket, similar_tickets, hits

    def problematic_tickets(self, for_days=0, year="", week_numbers=""):
        problematic_tickets = {}
        for jira_id in self.tickets:
            ticket = self.tickets[jira_id]
            is_in_range = self.ticket_is_in_range(ticket, for_days, year, week_numbers)
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

    def rank_projects_and_versions(self, hours_per_project, project_ticket_count, hours_per_version, projects_per_version):

        score_projects = {}
        for project_hours in hours_per_project:
            project_name = project_hours[0]
            score_projects[project_name] = {
                'hours': project_hours[1],
                'count': project_ticket_count[project_name]
            }

        rank_projects = {}
        for project_name in score_projects:
            rank = self.calculate_rank(project_name, score_projects)
            if rank is not None:
                rank_projects[project_name] = rank

        score_versions = {}
        for version_hours in hours_per_version:
            version_name = version_hours[0]
            score_versions[version_name] = {
                'hours': version_hours[1],
                'count': len(projects_per_version[version_name])
            }

        rank_versions = {}
        for version_name in score_versions:
            rank = self.calculate_rank(version_name, score_versions)
            if rank is not None:
                rank_versions[version_name] = rank

        return rank_projects, rank_versions

    def calculate_rank(self, target, all_scores):

        ranking_percentage = {
            'A+': 5,
            'A': 10,
            'B': 20,
            'C': 50,
            'D': 70,
            'E': 80,
            'F': 90
        }

        rank = None
        if target in all_scores:
            target_score = all_scores[target]

            all_hours = list(all_scores[name]['hours'] for name in all_scores)
            all_counts = list(all_scores[name]['count'] for name in all_scores)
            max_hours = float(max(all_hours))
            max_counts = float(max(all_counts))

            percentage_hours = target_score['hours'] / max_hours * 100
            percentage_count = target_score['count'] / max_counts * 100
            rank_hours = 'F'
            rank_count = 'F'
            for rank_mark in ranking_percentage:
                ranking_percent = ranking_percentage[rank_mark]
                if ranking_percent > percentage_hours:
                    rank_hours = rank_mark
                    break
            for rank_mark in ranking_percentage:
                ranking_percent = ranking_percentage[rank_mark]
                if ranking_percent > percentage_count:
                    rank_count = rank_mark
                    break

            rank = {
                'target': target,
                'rank': [rank_hours, rank_count]
            }

        return rank

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

    def ticket_is_in_range(self, ticket, for_days=0, year="", week_numbers=""):
        is_in_range = False
        time_updated = self.timestamp_from_ticket_time(ticket['Created'])
        current_time_stamp = datetime.datetime.now().timestamp()
        if for_days > 0:
            max_gap = for_days * 24 * 60 * 60
            is_in_range = time_updated >= (current_time_stamp - max_gap)
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

        return is_in_range

    @staticmethod
    def timestamp_from_ticket_time(ticket_time):
        if ticket_time is None:
            return 0
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
        for ticket_id in tickets:
            ticket = tickets[ticket_id]
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
        for ticket_id in tickets:
            ticket = tickets[ticket_id]
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

    def rank_ticket(self, ticket, tickets):
        normalized_ticket = self.normalize_ticket_for_ranks(ticket)
        normalized_tickets = self.normalize_tickets_for_ranks(tickets)
        print(normalized_ticket)

        """TODO: TBI"""
        return 'A+'

    def normalize_tickets_for_ranks(self, tickets):
        for ticket_id in tickets:
            tickets[ticket_id] = self.normalize_ticket_for_ranks(tickets[ticket_id])
        return tickets

    def normalize_ticket_for_ranks(self, ticket):
        closed_count = 0
        for state in ticket['Status']:
            if state['type'] in ['Fertig', 'Final abgeschlossen', 'Schliessen', 'Schließen', 'Closed', 'Gelöst', 'Done']:
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
