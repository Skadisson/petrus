from bin.service import Analyze
from bin.service import Cache
from bin.service import Environment
from bin.service import Docx
import json


class Trend:
    """Trend calculator"""

    def __init__(self, months=0, year="", week_numbers=""):
        self.months = float(months)
        self.year = str(year)
        self.week_numbers = str(week_numbers)
        self.cache = Cache.Cache()
        self.environment = Environment.Environment()

    def analyze_trend(self):
        analyze = Analyze.Analyze()
        days = self.months * 30
        hours_per_project = analyze.hours_per_project(days, self.year, self.week_numbers)
        hours_per_type = analyze.hours_per_type(days, self.year, self.week_numbers)
        hours_per_version, projects_per_version = analyze.hours_per_version(days, self.year, self.week_numbers)
        hours_total = analyze.hours_total(days, self.year, self.week_numbers)
        ticket_count = analyze.ticket_count(days, self.year, self.week_numbers)
        hours_per_ticket = analyze.hours_per_ticket(days, self.year, self.week_numbers)
        problematic_tickets = analyze.problematic_tickets(days, self.year, self.week_numbers)
        accuracy = analyze.accuracy(days, self.year, self.week_numbers)
        self.output_trend_json(ticket_count, hours_total, hours_per_project, hours_per_type, hours_per_version, projects_per_version, problematic_tickets, accuracy)
        return hours_per_project, hours_total, ticket_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, accuracy

    def generate_word_cloud(self):
        analyze = Analyze.Analyze()
        word_count, word_relations = analyze.word_count_and_relations()
        word_cloud = {
            'word_count': word_count,
            'word_relations': word_relations
        }
        self.output_word_cloud_json(word_cloud)
        return word_cloud

    def run(self):
        success = True
        hours_per_project = None
        hours_total = None
        ticket_count = None
        hours_per_type = None
        hours_per_version = None
        hours_per_ticket = None
        word_cloud = None
        docx_path = None
        accuracy = None
        projects_per_version = None

        try:
            hours_per_project, hours_total, ticket_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, accuracy = \
                self.analyze_trend()
            word_cloud = self.generate_word_cloud()
            docx_path = self.output_docx(hours_per_project, hours_total, ticket_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, accuracy)
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)
            success = False

        items = [{
            'ticket_count': ticket_count,
            "accuracy": accuracy,
            'hours_total': hours_total,
            'hours_per_project': hours_per_project,
            'hours_per_type': hours_per_type,
            'hours_per_version': hours_per_version,
            'projects_per_version': projects_per_version,
            'hours_per_ticket': hours_per_ticket,
            'word_cloud': word_cloud,
            'docx_path': docx_path
        }]
        return items, success

    def output_trend_json(self, ticket_count, hours_total, hours_per_project, hours_per_type, hours_per_version, projects_per_version, problematic_tickets, accuracy):

        trend_file = self.environment.get_path_trend()
        tickets_per_hour = ticket_count / hours_total
        payed_hours = 0.0
        un_payed_hours = 0.0

        for ticket_type in hours_per_type:
            if ticket_type[0] in ['Fehler', 'Maintenance']:
                un_payed_hours += ticket_type[1]
            elif ticket_type[0] in ['Serviceanfrage', 'Aufgabe', 'Media Service']:
                payed_hours += ticket_type[1]

        trend_content = {
            "tickets-tracked": ticket_count,
            "accuracy": accuracy,
            "hours-total": hours_total,
            "hot-projects": hours_per_project,
            "payed-hours": payed_hours,
            "un-payed-hours": un_payed_hours,
            "tickets-per-hour": tickets_per_hour,
            "hours-per-version": hours_per_version,
            "projects-per-version": projects_per_version,
            "problematic-tickets": problematic_tickets
        }

        file = open(trend_file, "w+")
        json.dump(obj=trend_content, fp=file)
        file.close()

    def output_word_cloud_json(self, word_cloud):
        word_cloud_output = []
        for source_word in word_cloud['word_relations']:
            for target_word in word_cloud['word_relations'][source_word]:
                word_cloud_output.append({
                    "source": source_word,
                    "target": target_word,
                    "weight": word_cloud['word_count'][source_word]
                })
        word_cloud_file = self.environment.get_path_word_cloud()
        file = open(word_cloud_file, "w+")
        json.dump(obj=word_cloud_output, fp=file)
        file.close()

    def output_docx(self, hours_per_project, hours_total, ticket_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, accuracy):
        docx_generator = Docx.Docx()
        docx_generator.place_headline()
        docx_generator.place_stats(ticket_count, hours_total, hours_per_type, self.months, accuracy)
        docx_generator.place_type_weight(hours_per_version, projects_per_version, self.months)
        docx_generator.place_versions(hours_per_version, self.months)
        docx_generator.place_projects(hours_per_project, self.months)
        docx_generator.place_tickets(hours_per_ticket, self.months)
        docx_path = docx_generator.save()

        return docx_path
