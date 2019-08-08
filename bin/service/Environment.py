import yaml
from yaml import CLoader as Loader


class Environment:
    """Environmental variable library"""

    def __init__(self, base_path):
        self.base_path = base_path

    def get_service_host(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['host']

    def get_service_port(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['port']

    def load_yaml(self, name):
        file = open("{}env\\{}.yaml".format(self.base_path, name), "r", encoding='utf8')
        return yaml.load(file, Loader=Loader)
