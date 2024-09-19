import time
from bin.service import Cache, LangChainOllama


def main():
    cache = Cache.Cache()
    start = time.time()
    print(f">>> starting training")
    ollama = LangChainOllama.LangChainOllama()
    unlearned_jira_tickets = cache.get_unlearned_jira_tickets()
    ollama.train_jira(list(unlearned_jira_tickets))
    minutes = round((time.time() - start) / 60, 2)
    print(f">>> completed training ollama with {len(list(unlearned_jira_tickets))} jira tickets after {minutes} minutes")



if __name__ == "__main__":
    main()