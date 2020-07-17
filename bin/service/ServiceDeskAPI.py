from bin.service import Environment
from bin.service import JiraSignature
from bin.service import Cache
import oauth2 as oauth
from urllib import parse
import json


class ServiceDeskAPI:
    """Service Desk API class"""

    def __init__(self):
        self.environment = Environment.Environment()
        self.token = None
        self.consumer = None
        self.client = None
        self.cache = Cache.Cache()
        self.init_api()

    def init_api(self):
        self.init_consumer()
        self.init_client()

    def init_consumer(self):
        consumer_key = self.environment.get_endpoint_consumer_key()
        consumer_secret = self.environment.get_endpoint_consumer_secret()
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)

    def init_client(self):
        tries = 3
        while self.token is None and tries > 0:
            self.retrieve_token()
            tries -= 1
        if self.token is None or tries == 0:
            raise Exception("Unable to retrieve sd api token, shutting down.")
        self.client = oauth.Client(self.consumer, self.token)
        self.client.set_signature_method(JiraSignature.JiraSignature())

    def retrieve_token(self):
        self.token = self.cache.load_token()
        if self.token is None or self.is_token_valid(self.token) is False:
            self.retrieve_token_url()

    def retrieve_token_url(self):
        request_token_url = self.environment.get_endpoint_request_token()
        self.client = oauth.Client(self.consumer)
        self.client.set_signature_method(JiraSignature.JiraSignature())
        resp, content = self.client.request(request_token_url, "POST")
        if resp['status'] != '200':
            raise Exception("Invalid response %s: %s" % (resp['status'],  content))
        request_token = dict(parse.parse_qsl(content))
        request_token_string = request_token[b'oauth_token'].decode("utf-8")
        request_secret_string = request_token[b'oauth_token_secret'].decode("utf-8")
        authorize_url = self.environment.get_endpoint_authorize()
        print("%s?oauth_token=%s" % (authorize_url, request_token_string))
        input('Please visit the URL and hit Enter')
        token = self.get_access_token(request_token_string, request_secret_string)
        token_is_valid = self.is_token_valid(token)
        if not token_is_valid:
            raise Exception("Right violation - shutting down")
        else:
            self.cache_token(token)
        self.token = token

    def get_access_token(self, request_token, request_secret):
        access_token_url = self.environment.get_endpoint_access_token()
        token = oauth.Token(request_token, request_secret)
        self.client = oauth.Client(self.consumer, token)
        self.client.set_signature_method(JiraSignature.JiraSignature())
        resp, content = self.client.request(access_token_url, "POST")
        access_token_response = dict(parse.parse_qsl(content))
        if b'oauth_problem' in access_token_response:
            access_problem = access_token_response[b'oauth_problem'].decode("utf-8")
            self.cache.add_log_entry(self.__class__.__name__, access_problem)
            raise Exception("No rights")
        access_token_final = access_token_response[b'oauth_token'].decode("utf-8")
        access_secret_final = access_token_response[b'oauth_token_secret'].decode("utf-8")
        access_token = oauth.Token(access_token_final, access_secret_final)
        return access_token

    @staticmethod
    def cache_token(token):
        cache = Cache.Cache()
        cache.store_token(token)

    def is_token_valid(self, request_token_string):
        self.client = oauth.Client(self.consumer, request_token_string)
        self.client.set_signature_method(JiraSignature.JiraSignature())
        resp, content = self.request_info()
        if resp['status'] == '500':
            self.cache.add_log_entry(self.__class__.__name__, "Jira responded with status 500")
        return resp['status'] == '200'

    def request_ticket_data(self, jira_key):
        ticket_endpoint = self.environment.get_endpoint_ticket()
        data_url = ticket_endpoint.format(jira_key)
        response, content = self.client.request(data_url, "GET")
        if response['status'] != '200':
            raise Exception("Request failed with status code {}".format(response['status']))
        return content.decode("utf-8")

    def request_service_jira_keys(self, offset=0, max_results=100, project='SERVICE'):
        jira_keys = {}

        tickets_endpoint = self.environment.get_endpoint_tickets()
        data_url = tickets_endpoint.format(project, max_results, offset)
        response, content = self.client.request(data_url, "GET")
        if response['status'] != '200' or content is False:
            raise Exception("Request failed with status code {}".format(response['status']))
        response_data = content.decode("utf-8")
        raw_data = json.loads(response_data)
        if 'issues' in raw_data:
            for issue in raw_data['issues']:
                jira_keys[issue['id']] = issue['key']

        return jira_keys

    def request_ticket_status(self, mapped_ticket):
        status_endpoint = self.environment.get_endpoint_status()
        status_url = status_endpoint.format(mapped_ticket['ID'])
        response, content = self.client.request(status_url, "GET")
        if response['status'] != '200':
            mapped_ticket['Status'] = None
            return mapped_ticket
        status_history_raw = content.decode("utf-8")
        mapped_ticket['Status'] = json.loads(status_history_raw)
        return mapped_ticket

    def request_ticket_worklog(self, mapped_ticket):
        worklog_endpoint = self.environment.get_endpoint_worklog()
        worklog_url = worklog_endpoint.format(mapped_ticket['ID'])
        response, content = self.client.request(worklog_url, "GET")
        if response['status'] != '200':
            mapped_ticket['Worklog'] = None
            return mapped_ticket
        worklog_raw = content.decode("utf-8")
        mapped_ticket['Worklog'] = json.loads(worklog_raw)
        return mapped_ticket

    def request_ticket_sla(self, mapped_ticket):
        sla_endpoint = self.environment.get_endpoint_sla()
        sla_url = sla_endpoint.format(mapped_ticket['ID'])
        response, content = self.client.request(sla_url, "GET")
        if response['status'] != '200':
            mapped_ticket['SLA'] = None
            return mapped_ticket
        sla_raw = content.decode("utf-8")
        mapped_ticket['SLA'] = json.loads(sla_raw)
        return mapped_ticket

    def request_ticket_comments(self, mapped_ticket):
        comment_endpoint = self.environment.get_endpoint_comment()
        comment_url = comment_endpoint.format(mapped_ticket['ID'])
        response, content = self.client.request(comment_url, "GET")
        if response['status'] != '200':
            mapped_ticket['Comments'] = None
            return mapped_ticket
        comments_raw = content.decode("utf-8")
        mapped_ticket['Comments'] = json.loads(comments_raw)
        return mapped_ticket

    def request_info(self):
        info_endpoint = self.environment.get_endpoint_info()
        response, content = self.client.request(info_endpoint, "GET")
        return response, content

    def post_ticket_comment(self, jira_id, priority, days_to_go):
        comment = 'Wir arbeiten im Customer Service in Warteschlangen um auch bei starker Nachfrage zeitgerecht reagieren zu können, hierbei ist die Priorität des Ticket ausschlaggebend. Mit der aktuellen Priorität "{}" wird das Ticket voraussichtlich in {} Tag(en) bearbeitet werden. Sollte das Thema allerdings dringend sein, antworten Sie bitte auf diese automatisierte Information, damit ein Customer Service Mitarbeiter die Priorität erhöhen kann. Ansonsten können Sie diese Information ignorieren.'.format(priority, days_to_go)
        if self.cache.comment_exists(jira_id):
            return True

        ticket_endpoint = self.environment.get_endpoint_comment().format(jira_id)
        request_content = {
            'body': comment,
            'public': False
        }
        request_body = json.dumps(request_content)
        body = request_body.encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        resp, content = self.client.request(ticket_endpoint, headers=headers, method="POST", body=body)
        state = int(resp.get('status'))
        success = state in [201, 204]

        if success:
            self.cache.store_comment(jira_id, comment)

        return success

    def update_ticket_times(self, jira_id, estimation, mapped_ticket):
        if mapped_ticket['Time_Spent'] is not None:
            time_spent = float(mapped_ticket['Time_Spent'])
        else:
            time_spent = 0.0
        estimation = float(estimation)
        ticket_endpoint = self.environment.get_endpoint_ticket().format(jira_id)
        remaining_time = self.calculate_remaining_time(estimation, time_spent)
        estimation_float_hours = self.seconds_to_hours(estimation)
        remaining_float_hours = self.seconds_to_hours(remaining_time)
        estimation_hours = int(estimation_float_hours)
        estimation_minutes = round((float(estimation_float_hours) - estimation_hours) * 60, 0)
        remaining_hours = int(remaining_float_hours)
        remaining_minutes = round((float(remaining_float_hours) - remaining_hours) * 60, 0)
        request_content = {
            "fields": {
                'timetracking': {
                    'originalEstimate': '{}h {}m'.format(estimation_hours, estimation_minutes).replace('.', ','),
                    'remainingEstimate': '{}h {}m'.format(remaining_hours, remaining_minutes).replace('.', ',')
                }
            }
        }
        request_body = json.dumps(request_content)
        body = request_body.encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        resp, content = self.client.request(ticket_endpoint, headers=headers, method="PUT", body=body)
        state = int(resp.get('status'))
        success = state in [201, 204]

        return success

    @staticmethod
    def seconds_to_hours(seconds):
        return seconds / 60 / 60

    @staticmethod
    def calculate_remaining_time(estimation, time_spent):
        remaining = estimation - time_spent
        if remaining <= 0:
            remaining = 0
        return remaining
