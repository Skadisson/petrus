from bin.service import Environment
import urllib.request
import json
import time


class GitlabAPI:
    """Gitl API class"""

    def __init__(self):
        self.environment = Environment.Environment()

    def request_all_commits(self, cache):

        private_token = self.environment.get_endpoint_git_private_token()
        url = self.environment.get_endpoint_git_projects()

        commits = {}
        page = 0
        run = True
        while run:
            time.sleep(0.25)
            page += 1
            parsed_url = url.format(private_token, page)
            projects = self.git_request(parsed_url)
            if len(projects) > 0:
                for project in projects:
                    project_commits = self.get_project_commits(project['id'])
                    for project_commit in project_commits:
                        commit = {
                            'title': project_commit['title'],
                            'text': project_commit['message'],
                            'date': project_commit['authored_date'],
                            'project': project['id']
                        }
                        self.cache_commit(cache, project_commit['id'], commit)
                        commits[project_commit['id']] = commit
            else:
                run = False

        return commits

    def get_project_commits(self, project_id):
        private_token = self.environment.get_endpoint_git_private_token()
        url = self.environment.get_endpoint_git_commits()

        commits = []
        page = 0
        run = True
        while run:
            page += 1
            parsed_url = url.format(project_id, private_token, page)
            project_commits = self.git_request(parsed_url)
            if len(project_commits) > 0:
                for project_commit in project_commits:
                    commits.append(project_commit)
            else:
                run = False

        return commits

    @staticmethod
    def git_request(url):
        f = urllib.request.urlopen(url)
        json_raw = f.read().decode('utf-8')
        return json.loads(json_raw)

    @staticmethod
    def cache_commit(cache, identifier, commit):
        cached_commits = cache.load_cached_commits()
        cached_commits[identifier] = commit
        cache.store_commits(cached_commits)