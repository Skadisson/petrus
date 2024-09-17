import yaml
import os


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

    def get_service_projects(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['projects']

    def get_service_spaces(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['spaces']

    def get_path_private_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['private_key']

    def get_path_public_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['public_key']

    def get_path_token(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['token']

    def get_endpoint_ticket(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['ticket']

    def get_endpoint_field(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['field']

    def get_endpoint_board(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['board']

    def get_endpoint_tickets(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['tickets']

    def get_endpoint_confluence(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['confluence']

    def get_endpoint_user(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['user']

    def get_endpoint_app_key(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['app_key']

    def get_endpoint_basic_token(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['basic_token']

    def get_endpoint_time(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['time']

    def get_endpoint_comment(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['comment']

    def get_map_ticket(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Ticket']

    def get_map_values(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Values']

    def get_map_keys(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Keys']

    def get_map_categories(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Categories']

    def get_map_state(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['State']

    def get_map_relation(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['Relation']

    def get_map_dates_of_horror(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['DatesOfHorror']

    def get_endpoint_ticket_link(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['ticket_link']

    def get_path_lost_jira_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['lost_jira_key']

    def get_path_mirror(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['mirror']

    def get_path_log(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['log']

    def get_path_jira_log(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['jira_log']

    def get_path_plot(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['plot']

    def get_path_graph(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['graph']

    def get_path_trend(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['trend']

    def get_path_word_cloud(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['word_cloud']

    def load_yaml(self, name):
        file = open("{}env\\{}.yaml".format(self.base_path, name), "r", encoding='utf8')
        return yaml.load(file, Loader=yaml.FullLoader)
