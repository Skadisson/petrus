from bin.service import Analyze
from bin.service import Cache
from bin.service import Environment
from bin.service import Docx
import json


class Trend:
    """Trend calculator"""

    def __init__(self, months=0, year="", week_numbers="", start=0):
        self.start = int(start)
        self.months = float(months)
        self.year = str(year)
        self.week_numbers = str(week_numbers)
        self.cache = Cache.Cache()
        self.environment = Environment.Environment()

    def analyze_trend(self):
        analyze = Analyze.Analyze()
        days = self.months * 30
        tickets = analyze.get_yer_tickets()
        filtered_tickets = analyze.filter_tickets_for_range(tickets, days, self.year, self.week_numbers, self.start)
        hours_per_project, project_ticket_count = analyze.hours_per_project(filtered_tickets)
        hours_per_system, system_ticket_count, system_versions = analyze.hours_per_system(filtered_tickets)
        payed_unpayed = analyze.payed_unpayed(filtered_tickets)
        plot_data = analyze.plot_data(filtered_tickets)
        hours_per_type = analyze.hours_per_type(filtered_tickets)
        hours_total = analyze.hours_total(filtered_tickets)
        ticket_count, internal_count, external_count = analyze.ticket_count(filtered_tickets)
        hours_per_ticket = analyze.hours_per_ticket(filtered_tickets)
        lifetime_per_ticket = analyze.lifetime_per_ticket(filtered_tickets)
        top_5_ticket_ranks, bottom_5_ticket_ranks = analyze.top_and_bottom_tickets(filtered_tickets, 5)
        total_score = analyze.score_tickets(filtered_tickets)

        return hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, system_versions, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_ticket, lifetime_per_ticket, top_5_ticket_ranks, bottom_5_ticket_ranks, plot_data, payed_unpayed, total_score

    def run(self):
        success = True
        hours_per_project = None
        project_ticket_count = None
        hours_per_system = None
        system_ticket_count = None
        hours_total = None
        ticket_count = None
        hours_per_type = None
        hours_per_version = None
        hours_per_ticket = None
        lifetime_per_ticket = None
        docx_path = None
        projects_per_version = None
        internal_count = None
        external_count = None
        system_versions = None
        general_summary = None
        total_score = 0

        try:
            hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, system_versions, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_ticket, lifetime_per_ticket, top_5_ticket_ranks, bottom_5_ticket_ranks, plot_data, payed_unpayed, total_score = \
                self.analyze_trend()
            docx_path = self.output_docx(hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, system_versions, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_ticket, lifetime_per_ticket, top_5_ticket_ranks, bottom_5_ticket_ranks, plot_data, payed_unpayed, total_score)
        except Exception as e:
            self.cache.add_log_entry(self.__class__.__name__, e)
            success = False

        items = [{
            'ticket_count': ticket_count,
            'internal_tickets': internal_count,
            'external_tickets': external_count,
            'hours_total': hours_total,
            'hours_per_project': hours_per_project,
            "project_ticket_count": project_ticket_count,
            'hours_per_system': hours_per_system,
            "system_ticket_count": system_ticket_count,
            'hours_per_type': hours_per_type,
            'hours_per_version': hours_per_version,
            'projects_per_version': projects_per_version,
            'hours_per_ticket': hours_per_ticket,
            'lifetime_per_ticket': lifetime_per_ticket,
            'docx_path': docx_path,
            "system_versions": system_versions,
            "total_score": total_score
        }]
        return items, success

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

    def output_docx(self, hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, system_versions, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_ticket, lifetime_per_ticket, top_5_ticket_ranks, bottom_5_ticket_ranks, plot_data, payed_unpayed, total_score):
        docx_generator = Docx.Docx()
        docx_generator.place_headline()
        docx_generator.place_type_pie_chart(hours_per_type)
        docx_generator.place_stats(ticket_count, internal_count, external_count, hours_total, lifetime_per_ticket, hours_per_type, total_score, top_5_ticket_ranks, bottom_5_ticket_ranks, self.months)
        docx_generator.place_plot(plot_data)
        docx_generator.place_payed_unpayed_pie_chart(payed_unpayed, self.months)
        docx_generator.place_projects(hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, system_versions, self.months)
        docx_generator.place_tickets(hours_per_ticket, self.months)
        docx_generator.place_page_break()
        docx_path = docx_generator.save()

        return docx_path
