
import json
import re
import os
from db.mongodb_connector import client

# Define the database name
db_name = 'sdg_database_clusters'

# Check if the database exists and drop it if it does
if db_name in client.list_database_names():
    client.drop_database(db_name)
    print(f"Database '{db_name}' has been deleted.")

# Create a new connection to the database
db = client[db_name]


sdg_dbs = []
print(os.getcwd())
f = open('./data/db/full_dataset_clusters.json')
data = json.load(f)

for sdg in data:
    print(sdg)
    pattern = r'\d+'
    db_name = f"sdg_{int(re.search(pattern, sdg).group()):02}"
    sdg_dbs.append({'index':int(re.search(pattern, sdg).group()), 'name':db_name})

    # create db per sdg
    cluster_db = db[db_name]



    levels = range(1,26,1)
    for level in levels:



        print(level)
         # create collection per level
        collection_name = f"level_{level:02}"
        collection = cluster_db[collection_name]


        level_str = str(level)
        if level_str in data[sdg]:

            centers = data[sdg][level_str].get('centers', [])
            sizes = data[sdg][level_str].get('sizes', [])
            labels = data[sdg][level_str].get('labels', [])

            for topic_index in range(0, level, 1):
                print(centers[topic_index], sizes[topic_index], labels[topic_index])

                # put documents into collection
                sdg_document = {
                    'cluster_id': f"{sdg}_level{level}_topic{topic_index+1}",
                    'size': sizes[topic_index],
                    'center': {'x': centers[topic_index][0], 'y': centers[topic_index][1]},
                    'name': f"topic{topic_index+1}",
                    'topic_name': labels[topic_index],
                }

                x = collection.insert_one(sdg_document)



f.close()
