import json
import os
import sys
import numpy as np
from tqdm import tqdm
from bson import ObjectId, BSON  # to handle $oid and BSON size calculation
from db.mongodb_connector import client

# Define the database and collection names
db_name = 'sdg_explanations'
source_collection_name = 'explanations'
target_collection_name = 'explanations_scaled'

# Create a new connection to the database
db = client[db_name]
source_collection = db[source_collection_name]
target_collection = db[target_collection_name]

# Iterate through documents in the source collection
for document in tqdm(source_collection.find()):
    # Calculate the size of the original document
    original_size = len(BSON.encode(document))

    # Copy the document to preserve all fields
    reduced_document = document.copy()

    # Round each number in the nested lists of token_scores
    token_scores = document.get("token_scores", [])
    token_scores_reduced = [
        [int(f"{round(10000*num)}") for num in sublist] for sublist in token_scores
    ]

    # Update the token_scores field in the copied document
    reduced_document["token_scores"] = token_scores_reduced

    # Calculate the size of the modified document
    reduced_size = len(BSON.encode(reduced_document))
    # Insert the modified document into the target collection
    target_collection.insert_one(reduced_document)

    if original_size - reduced_size > 0:
        print(f"Processed Zora OAI: {document.get('id')} - Original ID: {document.get('_id')} | Size Reduction: {original_size - reduced_size} bytes")
    #print(f"Original Document Size: {original_size} bytes")
    #print(f"Reduced Document Size: {reduced_size} bytes")
    #print(f"Size Reduction: {original_size - reduced_size} bytes")

print("All documents processed and uploaded to 'explanations_reduced'.")
