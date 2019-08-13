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
        if self.token is None or tries is 0:
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
            print(access_problem)
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
            print("Jira Server Error! Please try again later.")
        return resp['status'] == '200'

    def request_ticket_data(self, jira_key):
        ticket_endpoint = self.environment.get_endpoint_ticket()
        status_endpoint = self.environment.get_endpoint_status()
        data_url = ticket_endpoint.format(jira_key)
        validate_url = status_endpoint.format(jira_key)
        response, content = self.client.request(validate_url, "GET")
        if response['status'] != '200':
            raise Exception("Ticket {} does not exist".format(jira_key))
        response, content = self.client.request(data_url, "GET")
        if response['status'] != '200':
            raise Exception("Request failed with status code {}".format(response['status']))
        return content.decode("utf-8")

    def request_ticket_status(self, mapped_ticket):
        status_endpoint = self.environment.get_endpoint_status()
        status_url = status_endpoint.format(mapped_ticket['ID'])
        response, content = self.client.request(status_url, "GET")
        if response['status'] != '200':
            raise Exception("Request failed with status code {}".format(response['status']))
        status_history_raw = content.decode("utf-8")
        mapped_ticket['Status'] = json.loads(status_history_raw)
        return mapped_ticket

    def request_info(self):
        info_endpoint = self.environment.get_endpoint_info()
        response, content = self.client.request(info_endpoint, "GET")
        return response, content

    def update_ticket_times(self, jira_id, estimation, mapped_ticket):
        ticket_endpoint = self.environment.get_endpoint_ticket().format(jira_id)
        remaining_time = self.calculate_remaining_time(estimation, mapped_ticket)
        estimation_hours = self.seconds_to_hours(estimation)
        remaining_time_hours = self.seconds_to_hours(remaining_time)
        request_content = {
            "fields": {
                'timetracking': {
                    'originalEstimate': '{} h'.format(estimation_hours).replace('.', ','),
                    'remainingEstimate': '{} h'.format(remaining_time_hours).replace('.', ',')
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
    def calculate_remaining_time(estimation, mapped_ticket):
        if mapped_ticket is not None:
            if mapped_ticket["Time_Spent"] is None:
                mapped_ticket["Time_Spent"] = 0
            remaining = estimation - mapped_ticket["Time_Spent"]
            if remaining <= 0:
                remaining = 0
        else:
            remaining = 0

        return remaining
