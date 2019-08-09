from bin.service import ServiceDeskAPI


class Estimate:
    """Estimator"""

    def __init__(self, jira_key):
        self.jira_key = jira_key
        self.sd_api = ServiceDeskAPI.ServiceDeskAPI()

    def run(self):
        success = True
        items = []
        return items, success
