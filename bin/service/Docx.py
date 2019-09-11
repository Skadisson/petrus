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

        if months > 0:
            days = int(months * 30)
        else:
            days = 30
        paragraph = self.document.add_paragraph("In den letzten {} Tagen wurden ".format(days))
        paragraph.add_run("{} Tickets".format(ticket_count)).bold = True
        paragraph.add_run(" getrackt. Insgesamter getrackter Aufwand war ")
        paragraph.add_run("{} Stunden".format(hours_total)).bold = True
        paragraph.add_run(". Fehler-Support-Verhältnis war ")
        paragraph.add_run("{}:{}".format(bugfix_relation, support_relation)).bold = True
        paragraph.add_run(".")

    def place_projects(self, hours_per_project):
        self.document.add_heading('Projekte', level=1)
        self.document.add_paragraph('Im folgenden Aufwände dieses Monats pro Projekt.')
        for project_hours in hours_per_project:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(project_hours[0])).bold = True
            paragraph.add_run(" - {} Stunden".format(round(project_hours[1], ndigits=2)))

    def place_versions(self, hours_per_version):
        self.document.add_heading('Versionen', level=1)
        self.document.add_paragraph('Folgende brandbox Versionen haben diesen Monat Aufwände erzeugt.')
        for version_hours in hours_per_version:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(version_hours[0])).bold = True
            paragraph.add_run(" - {} Stunden".format(round(version_hours[1], ndigits=2)))

    def place_tickets(self, hours_per_ticket):
        self.document.add_heading('Tickets', level=1)
        self.document.add_paragraph('Eine Liste aller getrackten Tickets diesen Monat und deren bisherige Aufwände.')
        for ticket_hours in hours_per_ticket:
            paragraph = self.document.add_paragraph('')
            paragraph.add_run("{}".format(ticket_hours[0])).bold = True
            paragraph.add_run(" - {} Stunden".format(round(ticket_hours[1], ndigits=2)))

    def save(self):
        path = 'temp/trend.docx'
        self.document.save(path)

        return path
