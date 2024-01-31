from bin.service import Environment
from bin.service import Cache
import requests
import json
import datetime


class JiraRestAPI:
    def __init__(self):
        self.environment = Environment.Environment()
        self.cache = Cache.Cache()
        self.get_headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {self.environment.get_endpoint_basic_token()}"
        }
        self.put_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.environment.get_endpoint_basic_token()}"
        }
        self.board_id_cache = {}

    def request_ticket_data(self, jira_key):
        ticket_endpoint = self.environment.get_endpoint_ticket()
        data_url = ticket_endpoint.format(jira_key)
        response = requests.request(
            "GET",
            data_url,
            headers=self.get_headers
        )
        return json.loads(response.text)

    def request_service_jira_keys(self, offset=0, max_results=100, board='Service Board'):
        board_id = self.get_board_id_for_board(board)
        tickets_endpoint = self.environment.get_endpoint_tickets()
        data_url = tickets_endpoint.format(board_id, max_results, offset)
        response = requests.request(
            "GET",
            data_url,
            headers=self.get_headers
        )
        response_json = json.loads(response.text)

        jira_keys = {}
        for issue in response_json['issues']:
            if issue['key'] not in jira_keys:
                jira_keys[int(issue['id'])] = issue['key']

        return jira_keys

    def get_board_id_for_board(self, board_name):
        if board_name in self.board_id_cache:
            return self.board_id_cache

        board_endpoint = self.environment.get_endpoint_board()
        data_url = board_endpoint.format(board_name)
        response = requests.request(
            "GET",
            data_url,
            headers=self.get_headers
        )
        response_json = json.loads(response.text)

        board_id = 0
        for board in response_json['values']:
            if 'id' in board:
                board_id = board['id']
                break

        self.board_id_cache[board_name] = board_id
        return board_id

    def request_ticket_status(self, mapped_ticket):
        ticket_content = self.request_ticket_data(mapped_ticket['ID'])
        if 'status' in ticket_content:
            mapped_ticket['Status'] = ticket_content['status']
        else:
            mapped_ticket['Status'] = None
        return mapped_ticket

    def request_ticket_worklog(self, mapped_ticket):
        ticket_content = self.request_ticket_data(mapped_ticket['ID'])
        if 'worklog' in ticket_content and 'worklogs' in ticket_content['worklog']:
            mapped_ticket['Worklog'] = ticket_content['worklog']['worklogs']
        else:
            mapped_ticket['Worklog'] = None
        return mapped_ticket

    def request_ticket_comments(self, mapped_ticket):
        ticket_content = self.request_ticket_data(mapped_ticket['ID'])
        if 'comment' in ticket_content and 'comments' in ticket_content['comment']:
            mapped_ticket['Comments'] = ticket_content['comment']['comments']
        else:
            mapped_ticket['Comments'] = None
        return mapped_ticket

    def post_estimation_comment(self, jira_id, jira_key, days_to_go, today=False, similar_jira_keys=None, estimation=None):
        if estimation is None:
            return False

        if today:
            date = f"heute"
        else:
            end_date = datetime.date.today() + datetime.timedelta(days=days_to_go)
            date = f"{end_date.strftime('%Y/%m/%d')}"
        comment = f"Bearbeitung voraussichtlich bis {date}"
        if estimation > 0:
            hours = round(estimation / 60 / 60, 2)
            comment += f"\nKalkulierte Bearbeitungsdauer: {str(hours).replace('.', ',')} h"
        if similar_jira_keys is not None and len(similar_jira_keys) > 0:
            if jira_key in similar_jira_keys:
                same_id = similar_jira_keys.index(jira_key)
                del(similar_jira_keys[same_id])
            comment += f"\nÄhnliches Ticket: {similar_jira_keys[0]}"

        success = self.post_comment(jira_id, comment, "estimation")

        return success

    def post_comment(self, jira_id, comment, comment_type="estimation"):
        success = self.update_ticket_field(jira_id, comment, "customfield_12300")
        if success:
            self.cache.store_comment(jira_id, comment, comment_type)
        return success

    def update_ticket_times(self, jira_id, estimation):
        estimation = float(estimation)
        estimation_hours = self.seconds_to_hours(estimation)
        success = self.update_ticket_field(jira_id, str(estimation_hours), "estimation")
        return success

    def update_ticket_field(self, jira_id, value, field):
        field_endpoint = self.environment.get_endpoint_field()
        data_url = field_endpoint.format(jira_id, field)
        payload = json.dumps({
            "value": value
        })
        response = requests.request(
            "PUT",
            data_url,
            data=payload,
            headers=self.put_headers
        )
        response_data = json.loads(response.text)
        success = 'fieldId' in response_data and response_data['fieldId'] == field and 'value' in response_data and response_data['value'] == value
        return success

    @staticmethod
    def seconds_to_hours(seconds):
        return round(seconds / 60 / 60, 2)

    @staticmethod
    def calculate_remaining_time(estimation, time_spent):
        remaining = estimation - time_spent
        if remaining <= 0:
            remaining = 0
        return remaining
