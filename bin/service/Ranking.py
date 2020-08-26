class Ranking:
    """Ranking Calculator"""

    def normalize_tickets_for_ranks(self, tickets):
        for ticket_id in tickets:
            tickets[ticket_id] = self.normalize_ticket_for_ranks(tickets[ticket_id])
        return tickets

    @staticmethod
    def normalize_ticket_for_ranks(ticket):
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

    def score_tickets(self, tickets):
        for ticket_id in tickets:
            tickets[ticket_id] = self.score_ticket(tickets[ticket_id])
        return tickets

    def score_ticket(self, ticket):
        normalized_ticket = self.normalize_ticket_for_ranks(ticket)
        scoring = {
            'comments': 200,
            'breached': 200,
            'persons': 125,
            'relations': 125,
            'closed': 300,
            'support': 50
        }
        ticket_score = 0
        if normalized_ticket['comments'] < 10:
            ticket_score += scoring['comments']
        if normalized_ticket['breached'] == 0:
            ticket_score += scoring['breached']
        if normalized_ticket['persons'] < 3:
            ticket_score += scoring['persons']
        if normalized_ticket['relations'] < 2:
            ticket_score += scoring['relations']
        if normalized_ticket['closed'] == 1:
            ticket_score += scoring['closed']
        if normalized_ticket['support'] == 1:
            ticket_score += scoring['support']

        return ticket_score
