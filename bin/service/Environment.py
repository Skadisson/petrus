import yaml
import os

from yaml import CLoader as Loader


class Environment:
    """Environmental variable library"""

    def __init__(self):
        self.base_path = None
        self.init_base_path()

    def init_base_path(self):
        file_path = os.path.realpath(__file__)
        self.base_path = '\\'.join(file_path.split('\\')[0:-3]) + '\\'

    def get_bb_versions(self):
        service_yaml = self.load_yaml('bb_versions')
        return service_yaml

    def get_service_host(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['host']

    def get_service_port(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['port']

    def get_endpoint_consumer_key(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['consumer_key']

    def get_endpoint_consumer_secret(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['consumer_secret']

    def get_path_private_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['private_key']

    def get_path_public_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['public_key']

    def get_path_token(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['token']

    def get_endpoint_request_token(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['request_token']

    def get_endpoint_access_token(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['access_token']

    def get_endpoint_authorize(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['authorize']

    def get_endpoint_ticket(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['ticket']

    def get_endpoint_status(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['status']

    def get_endpoint_info(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['info']

    def get_map_ticket(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Ticket']

    def get_map_values(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Values']

    def get_map_state(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['State']

    def get_map_relation(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Relation']

    def get_path_cache(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['cache']

    def get_endpoint_ticket_link(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['ticket_link']

    def get_path_jira_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['jira_key']

    def get_path_mirror(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['mirror']

    def get_path_log(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['log']

    def get_path_plot(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['plot']

    def get_path_trend(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['trend']

    def get_path_word_cloud(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['word_cloud']

    def load_yaml(self, name):
        file = open("{}env\\{}.yaml".format(self.base_path, name), "r", encoding='utf8')
        return yaml.load(file, Loader=Loader)
