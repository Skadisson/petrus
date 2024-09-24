import requests, time
from requests.auth import HTTPBasicAuth
from bin.service import Environment, Cache, LangChainOllama


env = Environment.Environment()

BASE_URL = env.get_endpoint_confluence()
USERNAME = env.get_endpoint_user()
API_TOKEN = env.get_endpoint_app_key()
SPACES = env.get_service_spaces()

def run_request(url, params=None):
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN), params=params)

        if response.status_code == 200:
            page_data = response.json()
            return page_data
        else:
            print(f"Failed to retrieve data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_confluence_space(space):
    return run_request(f"{BASE_URL}/space/{space}")


def get_confluence_space_pages(space, offset=0, limit=20):
    return run_request(f"{BASE_URL}/space/{space}/content/page", {
            'start': offset,
            'limit': limit,
            'expand': 'space,body.storage'
        })


def get_content(content_id):
    return run_request(f"{BASE_URL}/content/{content_id}")


def get_history(content_id):
    return run_request(f"{BASE_URL}/content/{content_id}/history")


def main():
    cache = Cache.Cache()
    start = time.time()
    total_pages = 0
    limit = 20
    for space in SPACES:
        space_content = get_confluence_space(space)
        page_count = 0
        if space_content is not None:
            offset = 0
            updated_count = 0
            created_count = 0
            pages = get_confluence_space_pages(space, offset, limit)
            while len(pages['results']) > 0:
                for page_content in pages['results']:
                    page_history = get_history(page_content['id'])
                    entry = {
                        'space': space,
                        'id': page_content['id'],
                        'title': page_content['title'],
                        'body': page_content['body']['storage']['value'],
                        'date': page_history['lastUpdated']['when'],
                        'learned': False
                    }
                    created, updated = cache.update_confluence_entry(entry, True)
                    if updated:
                        updated_count += 1
                    if created:
                        created_count += 1
                    page_count += 1
                offset += limit
                pages = get_confluence_space_pages(space, offset)
                print(f">>> synced {page_count} pages in space {space}")
                if created_count > 0:
                    print(f">>> {updated_count} new confluence entries")
                if updated_count > 0:
                    print(f">>> updated {updated_count} confluence entries")
                time.sleep(10)
            print(f">>> total pages in space {space}: {page_count}")
            total_pages += page_count
    minutes = round((time.time() - start) / 60, 2)
    print(f">>> completed syncing {total_pages} total pages after {minutes} minutes")

    start = time.time()
    print(f">>> starting training")
    ollama = LangChainOllama.LangChainOllama()
    unlearned_confluence_entries = cache.get_unlearned_confluence_entries()
    ollama.train_confluence(list(unlearned_confluence_entries), total_pages)
    minutes = round((time.time() - start) / 60, 2)
    print(f">>> completed training ollama with {len(list(unlearned_confluence_entries))} confluence entries after {minutes} minutes")



if __name__ == "__main__":
    main()