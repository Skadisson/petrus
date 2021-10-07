import pymongo
import csv
import re


client = pymongo.MongoClient()
database = client.petrus
table_cache = database.cache
systems = table_cache.distinct('System')
csv_file = open("temp/systems.csv", "w", newline='')
writer = csv.writer(csv_file, delimiter=';')
writer.writerow(['System', 'Status'])
filtered_systems = []
sys_regex = re.compile("(https?:\/\/[a-z0-9\.\-]*)(\/admin[\.ph]*)?", re.IGNORECASE)
for system in systems:
    if system is not None and 'http' in system:
        matches = sys_regex.match(system)
        if matches is not None:
            system_url = ''
            for match in matches.groups():
                if match is not None:
                    system_url += match
            if system_url != '' and system_url not in filtered_systems:
                filtered_systems.append(system_url)
                writer.writerow([system_url, 'TODO'])
