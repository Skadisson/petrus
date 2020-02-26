from bin.service import Environment
import urllib.request
import json
import time


class ConfluenceAPI:
    """Confluence API class"""

    def __init__(self):
        self.environment = Environment.Environment()

    def request_all_documents(self, cache):

        url = self.environment.get_endpoint_confluence_list()

        documents = {}
        offset = 0
        found_item_count = 0
        run = True
        while run:
            time.sleep(0.25)
            try:
                parsed_url = url.format(offset)
                confluence_items = self.confluence_request(parsed_url)
                if 'results' in confluence_items:
                    found_item_count = confluence_items['size']
                    offset += found_item_count
                    if found_item_count > 0:
                        for confluence_item in confluence_items['results']:
                            time.sleep(0.05)
                            document = self.get_confluence_detail(confluence_item['id'])
                            self.cache_document(cache, confluence_item['id'], document)
                            documents[confluence_item['id']] = document
                    else:
                        run = False
                else:
                    run = False
            except Exception as e:
                cache.add_log_entry(self.__class__.__name__, e)
                time.sleep(1)
                offset -= found_item_count

        return documents

    def get_confluence_detail(self, confluence_id):
        detail_url = self.environment.get_endpoint_confluence_detail().format(confluence_id)
        confluence_detail = self.confluence_request(detail_url)
        formatted_detail = {
            'id': confluence_detail['id'],
            'title': confluence_detail['title'],
            'text': confluence_detail['body']['storage']['value'],
            'project': confluence_detail['container']['key'],
            'created': confluence_detail['version']['when'],
            'link': self.environment.get_endpoint_confluence_link().format(confluence_detail['_links']['webui'])
        }
        return formatted_detail

    @staticmethod
    def confluence_request(url):
        f = urllib.request.urlopen(url)
        json_raw = f.read().decode('utf-8')
        return json.loads(json_raw)

    @staticmethod
    def cache_document(cache, identifier, document):
        cached_documents = cache.load_cached_documents()
        cached_documents[identifier] = document
        cache.store_documents(cached_documents)
