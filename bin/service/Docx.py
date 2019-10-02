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

    def place_stats(self, ticket_count, hours_total, hours_per_type, months, accuracy):

        self.document.add_paragraph("").add_run("Durch Petrus automatisiert erstellt.").italic = True

        average = hours_total/ticket_count
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
        support_relation = round((support_hours / hours_sum) * 100)
        bugfix_relation = round((bugfix_hours / hours_sum) * 100)

        days = self.months_to_days(months)
        paragraph = self.document.add_paragraph("In den letzten ")
        paragraph.add_run("{} Tagen".format(days)).bold = True
        paragraph.add_run(" wurden ")
        paragraph.add_run("{} Tickets".format(ticket_count)).bold = True
        paragraph.add_run(" getrackt. Insgesamter getrackter Aufwand war ")
        paragraph.add_run("{} Stunden".format(hours_total)).bold = True
        paragraph.add_run(". Fehler-Support-Verhältnis war ")
        paragraph.add_run("{}:{}".format(bugfix_relation, support_relation)).bold = True
        paragraph.add_run(". Durchschnittliche Bearbeitungszeit pro Ticket war damit ")
        paragraph.add_run("{} Stunden".format(round(average, ndigits=2))).bold = True
        paragraph.add_run(".")
        """
        paragraph.add_run(". Petrus hat dabei durchschnittlich eine Genauigkeit von ")
        paragraph.add_run("{} %".format(round(accuracy, ndigits=0))).bold = True
        paragraph.add_run(" an den Tag gelegt.")
        """

    @staticmethod
    def months_to_days(months):
        if months > 0:
            days = int(months * 30)
        else:
            days = 30

        return days

    def place_projects(self, hours_per_project, months):
        days = self.months_to_days(months)
        self.document.add_heading('Projekte', level=1)
        self.document.add_paragraph('Im folgenden getrackte Aufwände der letzten {} Tage pro Projekt.'.format(days))
        for project_hours in hours_per_project:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(project_hours[0])).bold = True
            paragraph.add_run(" - {} Stunden".format(round(project_hours[1], ndigits=2)))

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
        self.document.add_heading('Tickets', level=1)
        self.document.add_paragraph('Eine Liste aller getrackten Tickets der letzten {} Tage und deren bisherige Aufwände.'.format(days))
        for ticket_hours in hours_per_ticket:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(ticket_hours[0])).bold = True
            if ticket_hours[1] > 0.0:
                paragraph.add_run(" - {} Stunden".format(round(ticket_hours[1], ndigits=2)))
            else:
                paragraph.add_run(" - n/a")

    def place_plot(self):
        plot_path = self.environment.get_path_plot()
        self.document.add_picture(plot_path, width=Inches(7))

    def save(self):
        path = 'temp/trend.docx'
        self.document.save(path)

        return path
