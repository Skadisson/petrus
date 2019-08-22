from bin.service import Analyze
from bin.service import Cache
from bin.service import Environment
import json


class Trend:
    """Trend calculator"""

    def __init__(self, months):
        self.months = float(months)
        self.cache = Cache.Cache()
        self.environment = Environment.Environment()

    def analyze_trend(self):
        analyze = Analyze.Analyze()
        days = self.months * 30
        hours_per_project = analyze.hours_per_project(days)
        hours_per_type = analyze.hours_per_type(days)
        hours_total = analyze.hours_total(days)
        ticket_count = analyze.ticket_count(days)
        problematic_tickets = analyze.problematic_tickets(days)
        self.output_trend_json(ticket_count, hours_total, hours_per_project, hours_per_type, problematic_tickets)
        return hours_per_project, hours_total, ticket_count, hours_per_type

    def generate_word_cloud(self):
        analyze = Analyze.Analyze()
        word_count, word_relations = analyze.word_count_and_relations()
        word_cloud = {
            'word_count': word_count,
            'word_relations': word_relations
        }
        self.output_word_cloud_json(word_cloud)

    def run(self):
        success = True
        hours_per_project = None
        hours_total = None
        ticket_count = None
        hours_per_type = None

        if self.months > 0:
            try:
                hours_per_project, hours_total, ticket_count, hours_per_type = self.analyze_trend()
                self.generate_word_cloud()
            except Exception as e:
                self.cache.add_log_entry(self.__class__.__name__, e)
                success = False

        else:
            success = False

        items = [{
            'ticket_count': ticket_count,
            'hours_total': hours_total,
            'hours_per_projects': hours_per_project,
            'hours_per_type': hours_per_type
        }]
        return items, success

    def output_trend_json(self, ticket_count, hours_total, hours_per_project, hours_per_type, problematic_tickets):

        trend_file = self.environment.get_path_trend()
        tickets_per_hour = ticket_count / hours_total
        payed_hours = 0.0
        un_payed_hours = 0.0
        bb5_hours = 0.0

        for ticket_type in hours_per_type:
            if ticket_type[0] in ['Fehler']:
                un_payed_hours += ticket_type[1]
            elif ticket_type[0] in ['Serviceanfrage', 'Aufgabe', 'Media Service']:
                payed_hours += ticket_type[1]
            elif ticket_type[0] in ['Maintenance']:
                bb5_hours += ticket_type[1]

        trend_content = {
            "tickets-tracked": ticket_count,
            "hours-total": hours_total,
            "hot-projects": hours_per_project,
            "payed-hours": payed_hours,
            "un-payed-hours": un_payed_hours,
            "bb5-hours": bb5_hours,
            "tickets-per-hour": tickets_per_hour,
            "problematic-tickets": problematic_tickets
        }

        file = open(trend_file, "w+")
        json.dump(obj=trend_content, fp=file)
        file.close()

    def output_word_cloud_json(self, word_cloud):
        word_cloud_file = self.environment.get_path_word_cloud()
        file = open(word_cloud_file, "w+")
        json.dump(obj=word_cloud, fp=file)
        file.close()
