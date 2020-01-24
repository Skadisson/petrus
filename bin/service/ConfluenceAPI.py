from bin.service import Environment
import urllib.request
import json
import time


class ConfluenceAPI:
    """Confluence API class"""

    def __init__(self):
        self.environment = Environment.Environment()

    def get_all_documents(self):

        url = self.environment.get_endpoint_confluence_list()

        documents = {}
        page = 0
        run = True
        while run:
            time.sleep(0.25)
            page += 1
            parsed_url = url.format(page)
            confluence_items = self.confluence_request(parsed_url)
            if 'results' in confluence_items and len(confluence_items['results']) > 0:
                for confluence_item in confluence_items['results']:
                    documents[confluence_item['id']] = self.get_confluence_detail(confluence_item['id'])
            else:
                run = False

        return documents

    def get_confluence_detail(self, confluence_id):
        detail_url = self.environment.get_endpoint_confluence_detail().format(confluence_id)
        confluence_detail = self.confluence_request(detail_url)
        formatted_detail = {
            'id': confluence_detail['id'],
            'title': confluence_detail['title'],
            'text': confluence_detail['body']['storage']['value'],
            'project': confluence_detail['container']['key'],
            'link': self.environment.get_endpoint_confluence_link().format(confluence_detail['_links']['webui'])
        }
        return formatted_detail

    @staticmethod
    def confluence_request(url):
        f = urllib.request.urlopen(url)
        json_raw = f.read().decode('utf-8')
        return json.loads(json_raw)
