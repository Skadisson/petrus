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
        time_spent = 0
        if 'Time_Spent' in ticket and ticket['Time_Spent'] is not None:
            time_spent = int(ticket['Time_Spent'])
        normalized_ticket = {
            'comments': len(ticket['Comments']),
            'breached': int(breached),
            'persons': persons,
            'relations': len(ticket['Related']),
            'closed': closed_count,
            'support': int(support),
            'time_spent': time_spent
        }
        return normalized_ticket

    def score_tickets(self, tickets):
        for ticket_id in tickets:
            tickets[ticket_id] = self.score_ticket(tickets[ticket_id])
        return tickets

    def score_ticket(self, ticket):
        normalized_ticket = self.normalize_ticket_for_ranks(ticket)
        ticket_score = 0
        if normalized_ticket['comments'] < 5:
            ticket_score += 50
        threshold = 10
        while normalized_ticket['comments'] > threshold:
            ticket_score += 100
            threshold += 10
        if normalized_ticket['breached'] == 0:
            ticket_score += 200
        threshold = 1
        while normalized_ticket['persons'] > threshold:
            ticket_score += threshold * 100
            threshold += 1
        hours = 1
        while int(normalized_ticket['time_spent']) > hours * 60 * 60:
            ticket_score += hours * 100
            hours += 1

        return ticket_score
