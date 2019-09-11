from docx import Document
from datetime import datetime


class Docx:
    """DOCX generator"""

    def __init__(self):
        self.document = Document()

    def place_headline(self):
        now = datetime.now()
        date = datetime.strftime(now, "%Y/%m/%d")
        self.document.add_heading("Support Report {}".format(date), 0)

    def place_stats(self, ticket_count, hours_total, hours_per_type, months):

        self.document.add_paragraph("").add_run("Durch Petrus automatisiert erstellt.").italic = True

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
        paragraph = self.document.add_paragraph("In den letzten {} Tagen wurden ".format(days))
        paragraph.add_run("{} Tickets".format(ticket_count)).bold = True
        paragraph.add_run(" getrackt. Insgesamter getrackter Aufwand war ")
        paragraph.add_run("{} Stunden".format(hours_total)).bold = True
        paragraph.add_run(". Fehler-Support-Verhältnis war ")
        paragraph.add_run("{}:{}".format(bugfix_relation, support_relation)).bold = True
        paragraph.add_run(".")

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
            paragraph.add_run(" - {} Stunden".format(round(ticket_hours[1], ndigits=2)))

    def save(self):
        path = 'temp/trend.docx'
        self.document.save(path)

        return path
