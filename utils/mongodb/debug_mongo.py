
import json
import re
import os
from collections import defaultdict

from db.mongodb_connector import client


# Define the database and collection names
db_name = 'sdg_explanations'
collection_name = 'explanations'

# Check if the database exists and drop it if it does
if db_name in client.list_database_names():
    print(f"Database '{db_name}' has is present.")


db = client.sdg_explanations
collection = db.explanations

# Dictionary to keep track of document _ids for each id field
id_map = defaultdict(list)

num_docs = 0

# Iterate through all documents in the collection
for document in collection.find():
    if "id" in document:
        num_docs += 1
        id_map[document["id"]].append(document["_id"])
    else:
        print(document)

# Find and print duplicates
duplicates = {key: ids for key, ids in id_map.items() if len(ids) > 1}

# Output duplicate document _ids
for id_value, _ids in duplicates.items():
    print(f"Duplicate id: {id_value}, Document _ids: {_ids}")

print(f"Total unique 'id' values: {len(id_map)}")
print(f"Total documents processed: {num_docs}")
print(f"Number of duplicate 'id' values: {len(duplicates)}")

# Find duplicates and delete the younger ones
for id_value, _ids in duplicates.items():
    if len(_ids) > 1:
        # Sort _ids by their natural order (ObjectId includes a timestamp)
        _ids.sort(reverse=True)

        # Delete the younger documents, keep the oldest
        for _id in _ids[1:]:
            collection.delete_one({"_id": _id})
            print(f"Deleted document with _id: {_id} for duplicate id: {id_value}")

print("Younger duplicates deleted successfully.")



