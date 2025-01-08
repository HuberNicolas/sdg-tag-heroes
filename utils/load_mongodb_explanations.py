import json
import os
from tqdm import tqdm
from bson import ObjectId  # to handle $oid
from db.mongodb_connector import client

# Define the database and collection names
db_name = 'sdg_explanations'
collection_name = 'explanations'

# Check if the database exists and drop it if it does
if db_name in client.list_database_names():
    client.drop_database(db_name)
    print(f"Database '{db_name}' has been deleted.")

# Create a new connection to the database
db = client[db_name]
collection = db[collection_name]

# Shell command:
"""
awk '{
  if (NR % 10000 == 1) {
    file = sprintf("split_part_%03d.json", int(NR/10000))
  }
  print $0 >> file
}' sdg_explanations.json
"""

# Function to convert $oid to ObjectId
def convert_oid(doc):
    if '_id' in doc and '$oid' in doc['_id']:
        doc['_id'] = ObjectId(doc['_id']['$oid'])
    return doc


# Directory containing the split files
split_files_directory = './data/db/explanations/'
split_files_prefix = 'split_part_'  # Prefix of the split files

# Iterate through each split file
for filename in tqdm(sorted(os.listdir(split_files_directory)), desc="Loading files"):
    if filename.startswith(split_files_prefix):
        file_path = os.path.join(split_files_directory, filename)

        # Load the JSON objects from the file
        with open(file_path, 'r') as f:
            data = [json.loads(line) for line in f]

        # Convert _id fields and insert documents
        data = [convert_oid(doc) for doc in data]
        collection.insert_many(data)

print(f"All data has been successfully loaded into the '{collection_name}' collection.")
