from docx import Document
from docx.shared import Inches
from datetime import datetime
from bin.service import Environment


class Docx:
    """DOCX generator"""

    def __init__(self):
        self.document = Document()
        self.environment = Environment.Environment()

    def place_headline(self):
        now = datetime.now()
        date = datetime.strftime(now, "%Y/%m/%d")
        self.document.add_heading("Support Report {}".format(date), 0)

    def place_stats(self, ticket_count, internal_count, external_count, hours_total, hours_per_type, months, pe_ticket_count, is_ticket_count):

        self.document.add_paragraph("").add_run("Durch Petrus automatisiert erstellt.").italic = True

        if ticket_count > 0.0:
            average = hours_total/ticket_count
        else:
            average = 0.0
        support_hours = 0.0
        bugfix_hours = 0.0
        for type_hours in hours_per_type:
            type = type_hours[0]
            hours = type_hours[1]
            if type in ['Fehler', 'Bug', 'Maintenance']:
                bugfix_hours += hours
            else:
                support_hours += hours
        hours_sum = support_hours + bugfix_hours
        hours_total = round(hours_total)
        if hours_sum > 0.0:
            support_relation = round((support_hours / hours_sum) * 100)
            bugfix_relation = round((bugfix_hours / hours_sum) * 100)
        else:
            support_relation = 50
            bugfix_relation = 50

        days = self.months_to_days(months)
        paragraph = self.document.add_paragraph("In den letzten ")
        paragraph.add_run("{} Tagen".format(days)).bold = True
        paragraph.add_run(" wurden ")
        paragraph.add_run("{} Tickets".format(ticket_count)).bold = True
        paragraph.add_run(" getrackt. Davon waren ")
        paragraph.add_run("{} Tickets von Mitarbeitern".format(internal_count)).bold = True
        paragraph.add_run(" und ")
        paragraph.add_run("{} Tickets von Kunden".format(external_count)).bold = True
        paragraph.add_run(". Insgesamter getrackter Aufwand war ")
        paragraph.add_run("{} Stunden".format(hours_total)).bold = True
        paragraph.add_run(". Fehler-Support-Verhältnis war ")
        paragraph.add_run("{}:{}".format(bugfix_relation, support_relation)).bold = True
        paragraph.add_run(". Durchschnittliche Bearbeitungszeit pro Ticket war damit ")
        paragraph.add_run("{} Stunden".format(round(average, ndigits=2))).bold = True
        paragraph.add_run(".")
        paragraph.add_run(f"Es wurden {pe_ticket_count} Tickets an die Produktentwicklung übertragen, {is_ticket_count} Tickets wurden an Individual Service übergeben.")

    @staticmethod
    def months_to_days(months):
        if months > 0:
            days = int(months * 30)
        else:
            days = 30

        return days

    def place_projects(self, hours_per_project, project_ticket_count, months):
        days = self.months_to_days(months)
        self.document.add_heading('Projekte', level=1)
        self.document.add_paragraph('Im folgenden getrackte Aufwände der letzten {} Tage pro Projekt.'.format(days))
        for project_hours in hours_per_project:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(project_hours[0])).bold = True
            paragraph.add_run(" - {} Stunden auf {} Tickets".format(round(project_hours[1], ndigits=2), project_ticket_count[project_hours[0]]))

    def place_systems(self, hours_per_system, system_ticket_count, months):
        days = self.months_to_days(months)
        self.document.add_heading('Systeme', level=1)
        self.document.add_paragraph('Im folgenden getrackte Aufwände der letzten {} Tage pro System.'.format(days))
        for system_hours in hours_per_system:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(system_hours[0])).bold = True
            paragraph.add_run(" - {} Stunden auf {} Tickets".format(round(system_hours[1], ndigits=2), system_ticket_count[system_hours[0]]))

    def place_type_weight(self, hours_per_version, projects_per_version, months):
        bb_versions = self.environment.get_bb_versions()
        weights = {}
        projects = {}
        for bb_type in bb_versions:
            weights[bb_type] = 0.0
        days = self.months_to_days(months)
        self.document.add_heading('Gewichtung', level=1)
        self.document.add_paragraph('Folgende brandbox Typen haben in {} Tagen getrackte Aufwände erzeugt.'.format(days))
        for version_hours in hours_per_version:
            version = version_hours[0]
            hours = round(version_hours[1], ndigits=2)
            for bb_type in bb_versions:
                bb_type_versions = bb_versions[bb_type].split(" ")
                if version in bb_type_versions:
                    weights[bb_type] += hours
                    if version in projects_per_version:
                        if bb_type not in projects:
                            projects[bb_type] = []
                        for project in projects_per_version[version]:
                            if project not in projects[bb_type]:
                                projects[bb_type].append(project)
        for bb_type in weights:
            bb_type_versions = bb_versions[bb_type].split(" ")
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{} ({})".format(bb_type, bb_type_versions[0] + ' - ' + bb_type_versions[-1])).bold = True
            paragraph.add_run(" - {} Stunden auf {} Projekte".format(weights[bb_type], len(projects[bb_type])))

    def place_versions(self, hours_per_version, months):
        days = self.months_to_days(months)
        self.document.add_heading('Versionen', level=1)
        self.document.add_paragraph('Folgende brandbox Versionen haben in den letzten {} Tagen getrackte Aufwände erzeugt.'.format(days))
        for version_hours in hours_per_version:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(version_hours[0])).bold = True
            paragraph.add_run(" - {} Stunden".format(round(version_hours[1], ndigits=2)))

    def place_tickets(self, hours_per_ticket, months):
        days = self.months_to_days(months)
        self.document.add_heading('SERVICE Tickets', level=1)
        self.document.add_paragraph('Eine Liste aller {} SERVICE Tickets der letzten {} Tage und deren bisherige Aufwände.'.format(len(hours_per_ticket), days))
        for ticket_hours in hours_per_ticket:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(ticket_hours[0])).bold = True
            if ticket_hours[1] > 0.0:
                paragraph.add_run(" - {} Stunden".format(round(ticket_hours[1], ndigits=2)))
            else:
                paragraph.add_run(" - n/a")

    def place_qs_tickets(self, qs_tickets_and_relations, months):
        days = self.months_to_days(months)
        self.document.add_heading('QS Tickets', level=1)
        count_qs = len(qs_tickets_and_relations)
        count_qs_service = 0
        service_tickets = []
        for qs_ticket in qs_tickets_and_relations:
            if len(qs_tickets_and_relations[qs_ticket]) > 0:
                count_qs_service += 1
                service_tickets += qs_tickets_and_relations[qs_ticket]
        if count_qs_service > 0:
            self.document.add_paragraph('Es wurden {} QS Tickets in den letzten {} Tagen erstellt, {} davon in Verbindung mit folgenden SERVICE Tickets:'.format(count_qs, days, count_qs_service))
            for service_ticket in service_tickets:
                paragraph = self.document.add_paragraph('')
                paragraph.add_run("{}".format(service_ticket)).bold = True
        else:
            self.document.add_paragraph('Es wurden {} QS Tickets in den letzten {} Tagen erstellt, keines davon in Verbindung mit SERVICE Tickets.'.format(count_qs, days))

    def place_devops_tickets(self, devops_tickets_and_relations, months):
        days = self.months_to_days(months)
        self.document.add_heading('DevOps Tickets', level=1)
        count_devops = len(devops_tickets_and_relations)
        count_devops_service = 0
        service_tickets = []
        for devops_ticket in devops_tickets_and_relations:
            if len(devops_tickets_and_relations[devops_ticket]) > 0:
                count_devops_service += 1
                service_tickets += devops_tickets_and_relations[devops_ticket]
        if count_devops_service > 0:
            self.document.add_paragraph('Es wurden {} DevOps Tickets in den letzten {} Tagen erstellt, {} davon in Verbindung mit folgenden SERVICE Tickets:'.format(count_devops, days, count_devops_service))
            for service_ticket in service_tickets:
                paragraph = self.document.add_paragraph('')
                paragraph.add_run("{}".format(service_ticket)).bold = True
        else:
            self.document.add_paragraph('Es wurden {} DevOps Tickets in den letzten {} Tagen erstellt, keines davon in Verbindung mit SERVICE Tickets.'.format(count_devops, days))

    def place_bb5_tickets(self, bb5_tickets_and_relations, months, bb5_hours_total, bb5_ticket_count):
        days = self.months_to_days(months)
        self.document.add_heading('BRANDBOX5 Tickets', level=1)
        count_bb5_service = 0
        if bb5_ticket_count > 0:
            average = round(bb5_hours_total/bb5_ticket_count)
        else:
            average = 0
        service_tickets = []
        for bb5_ticket in bb5_tickets_and_relations:
            if len(bb5_tickets_and_relations[bb5_ticket]) > 0:
                count_bb5_service += 1
                service_tickets += bb5_tickets_and_relations[bb5_ticket]
        if count_bb5_service > 0:
            self.document.add_paragraph('Es wurden {} BRANDBOX5 Tickets in den letzten {} Tagen erstellt, {} davon in Verbindung mit folgenden SERVICE Tickets:'.format(bb5_ticket_count, days, count_bb5_service))
            if average > 0:
                self.document.add_paragraph(f"Insgesamt mit einem Aufwand von {bb5_hours_total} Stunden, also durchschnittlich {average} Stunden pro Ticket.")
            for service_ticket in service_tickets:
                paragraph = self.document.add_paragraph('')
                paragraph.add_run("{}".format(service_ticket)).bold = True
        else:
            self.document.add_paragraph('Es wurden {} BRANDBOX5 Tickets in den letzten {} Tagen erstellt.'.format(bb5_ticket_count, days))
            if average > 0:
                self.document.add_paragraph(f"Insgesamt mit einem Aufwand von {bb5_hours_total} Stunden, also durchschnittlich {average} Stunden pro Ticket.")

    def place_plot(self):
        self.document.add_heading('Aufwände pro Kalender-Woche', level=1)
        plot_path = self.environment.get_path_plot()
        self.document.add_picture(plot_path, width=Inches(6))

    def save(self):
        path = 'temp/trend.docx'
        self.document.save(path)

        return path
