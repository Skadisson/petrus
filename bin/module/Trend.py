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
        hours_per_project, project_ticket_count, project_tickets = analyze.hours_per_project(days, self.year, self.week_numbers)
        hours_per_system, system_ticket_count, system_tickets = analyze.hours_per_system(days, self.year, self.week_numbers)
        project_scores = analyze.score_labeled_tickets(project_tickets)
        system_scores = analyze.score_labeled_tickets(system_tickets)
        hours_per_type = analyze.hours_per_type(days, self.year, self.week_numbers)
        hours_per_version, projects_per_version = analyze.hours_per_version(days, self.year, self.week_numbers)
        hours_total = analyze.hours_total(days, self.year, self.week_numbers)
        bb5_hours_total = analyze.bb5_hours_total(days, self.year, self.week_numbers)
        ticket_count, internal_count, external_count = analyze.ticket_count(days, self.year, self.week_numbers)
        pe_ticket_count = analyze.pe_ticket_count(days, self.year, self.week_numbers)
        is_ticket_count = analyze.is_ticket_count(days, self.year, self.week_numbers)
        bb5_ticket_count = analyze.bb5_ticket_count(days, self.year, self.week_numbers)
        hours_per_ticket = analyze.hours_per_ticket(days, self.year, self.week_numbers)
        top_5_ticket_ranks, bottom_5_ticket_ranks = analyze.top_and_bottom_tickets(days, self.year, self.week_numbers)
        qs_tickets_and_relations, cs_to_qs = analyze.qs_tickets_and_relations(days, self.year, self.week_numbers)
        devops_tickets_and_relations, cs_to_devops = analyze.devops_tickets_and_relations(days, self.year, self.week_numbers)
        bb5_tickets_and_relations = analyze.bb5_tickets_and_relations(days, self.year, self.week_numbers)
        problematic_tickets = analyze.problematic_tickets(days, self.year, self.week_numbers)
        self.output_trend_json(ticket_count, internal_count, external_count, hours_total, hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, hours_per_type, hours_per_version, projects_per_version, problematic_tickets, project_scores, system_scores, qs_tickets_and_relations, devops_tickets_and_relations, bb5_tickets_and_relations, bb5_hours_total, bb5_ticket_count, pe_ticket_count, is_ticket_count, cs_to_qs, cs_to_devops, top_5_ticket_ranks, bottom_5_ticket_ranks)
        return hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, project_scores, system_scores, qs_tickets_and_relations, devops_tickets_and_relations, bb5_tickets_and_relations, bb5_hours_total, bb5_ticket_count, pe_ticket_count, is_ticket_count, cs_to_qs, cs_to_devops, top_5_ticket_ranks, bottom_5_ticket_ranks

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
        docx_path = None
        projects_per_version = None
        internal_count = None
        external_count = None
        project_scores = None
        system_scores = None

        try:
            hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, project_scores, system_scores, qs_tickets_and_relations, devops_tickets_and_relations, bb5_tickets_and_relations, bb5_hours_total, bb5_ticket_count, pe_ticket_count, is_ticket_count, cs_to_qs, cs_to_devops, top_5_ticket_ranks, bottom_5_ticket_ranks = \
                self.analyze_trend()
            docx_path = self.output_docx(hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, qs_tickets_and_relations, devops_tickets_and_relations, bb5_tickets_and_relations, bb5_hours_total, bb5_ticket_count, pe_ticket_count, is_ticket_count, cs_to_qs, cs_to_devops, top_5_ticket_ranks, bottom_5_ticket_ranks)
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
            'docx_path': docx_path,
            'project_scores': project_scores,
            'system_scores': system_scores
        }]
        return items, success

    def output_trend_json(self, ticket_count, internal_count, external_count, hours_total, hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, hours_per_type, hours_per_version, projects_per_version, problematic_tickets, project_scores, system_scores, qs_tickets_and_relations, devops_tickets_and_relations, bb5_tickets_and_relations, bb5_hours_total, bb5_ticket_count, pe_ticket_count, is_ticket_count, cs_to_qs, cs_to_devops, top_5_ticket_ranks, bottom_5_ticket_ranks):

        trend_file = self.environment.get_path_trend()
        categories = self.environment.get_map_categories()
        if hours_total > 0.0:
            tickets_per_hour = ticket_count / hours_total
        else:
            tickets_per_hour = 0
        payed_hours = 0.0
        un_payed_hours = 0.0

        for ticket_type in hours_per_type:
            if ticket_type[0] in categories['Bug']:
                un_payed_hours += ticket_type[1]
            elif ticket_type[0] in categories['Support']:
                payed_hours += ticket_type[1]

        trend_content = {
            "tickets-tracked": ticket_count,
            "internal-tickets": internal_count,
            "external-tickets": external_count,
            "hours-total": hours_total,
            "hot-projects": hours_per_project,
            "project_ticket_count": project_ticket_count,
            "hours_per_system": hours_per_system,
            "system_ticket_count": system_ticket_count,
            "payed-hours": payed_hours,
            "un-payed-hours": un_payed_hours,
            "tickets-per-hour": tickets_per_hour,
            "hours-per-version": hours_per_version,
            "projects-per-version": projects_per_version,
            "problematic-tickets": problematic_tickets,
            "project_scores": project_scores,
            "system_scores": system_scores,
            "qs_tickets_and_relations": qs_tickets_and_relations,
            "devops_tickets_and_relations": devops_tickets_and_relations,
            "bb5_tickets_and_relations": bb5_tickets_and_relations,
            "bb5_hours_total": bb5_hours_total,
            "bb5_ticket_count": bb5_ticket_count,
            "pe_ticket_count": pe_ticket_count,
            "is_ticket_count": is_ticket_count,
            "cs_to_qs": cs_to_qs,
            "cs_to_devops": cs_to_devops,
            "top_5_ticket_ranks": top_5_ticket_ranks,
            "bottom_5_ticket_ranks": bottom_5_ticket_ranks
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

    def output_docx(self, hours_per_project, project_ticket_count, hours_per_system, system_ticket_count, hours_total, ticket_count, internal_count, external_count, hours_per_type, hours_per_version, projects_per_version, hours_per_ticket, qs_tickets_and_relations, devops_tickets_and_relations, bb5_tickets_and_relations, bb5_hours_total, bb5_ticket_count, pe_ticket_count, is_ticket_count, cs_to_qs, cs_to_devops, top_5_ticket_ranks, bottom_5_ticket_ranks):
        docx_generator = Docx.Docx()
        docx_generator.place_headline()
        docx_generator.place_stats(ticket_count, internal_count, external_count, hours_total, hours_per_type, self.months, pe_ticket_count, is_ticket_count, cs_to_qs, cs_to_devops)
        docx_generator.place_type_weight(hours_per_version, projects_per_version, self.months)
        docx_generator.place_versions(hours_per_version, self.months)
        docx_generator.place_projects(hours_per_project, project_ticket_count, self.months)
        docx_generator.place_systems(hours_per_system, system_ticket_count, self.months)
        docx_generator.place_qs_tickets(qs_tickets_and_relations, self.months)
        docx_generator.place_devops_tickets(devops_tickets_and_relations, self.months)
        docx_generator.place_bb5_tickets(bb5_tickets_and_relations, self.months, bb5_hours_total, bb5_ticket_count)
        docx_generator.place_top_tickets(top_5_ticket_ranks, self.months)
        docx_generator.place_bottom_tickets(bottom_5_ticket_ranks, self.months)
        docx_generator.place_tickets(hours_per_ticket, self.months)
        docx_path = docx_generator.save()

        return docx_path
