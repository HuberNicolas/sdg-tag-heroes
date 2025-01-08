import os
import json
import time
import pandas as pd
from sqlalchemy.orm import sessionmaker, joinedload
from db.mariadb_connector import engine as mariadb_engine
from models import SDGLabelSummary
from models.publications.publication import Publication
from utils.env_loader import load_env, get_env_variable
from openai import OpenAI

# Initialize OpenAI client
load_env('api.env')
client = OpenAI()


# Initialize database session
Session = sessionmaker(bind=mariadb_engine)

def fetch_publications_by_sdg(session, sdg_number):
    """
    Fetches all publications for a specific SDG goal where the label summary
    has a value of 1 for the given SDG.
    """
    if not 1 <= sdg_number <= 17:
        raise ValueError("SDG number must be between 1 and 17")

    sdg_field = f"sdg{sdg_number}"

    sdg_label_summaries = (
        session.query(SDGLabelSummary)
        .filter(getattr(SDGLabelSummary, sdg_field) == 1)
        .options(joinedload(SDGLabelSummary.publication))
        .limit(4)
        .all()
    )

    results = []
    for label_summary in sdg_label_summaries:
        publication = label_summary.publication
        if publication:
            results.append(publication)

    return results

def create_jsonl_file(file_name, publications):
    """
    Creates a JSONL file for OpenAI Batch API containing abstracts.
    """
    with open(file_name, 'w') as file:
        for pub in publications:
            abstract_text = pub.description
            file.write(json.dumps({
                "prompt": f"Analyze the following abstract and provide SDG relevance and confidence for each SDG (1–17):\n\n{abstract_text}",
                "completion": ""
            }) + '\n')

def upload_jsonl_file(jsonl_file_path):
    """
    Uploads a JSONL file to OpenAI for batch processing.
    """
    response = client.files.create(
        file=open(jsonl_file_path, "rb"),
        purpose="batch"
    )
    return response.id

def create_batch_job(file_id):
    """
    Creates a batch job for processing uploaded JSONL file.
    """
    response = client.batches.create(
        input_file_id=file_id,
        endpoint='/v1/completions',
        model="gpt-4",
        completion_window="24h"
    )
    return response.id

def monitor_batch_job(batch_id):
    """
    Monitors the batch job until it completes.
    """
    while True:
        status = client.batches.retrieve(batch_id)
        if status["status"] in ["completed", "failed"]:
            return status
        time.sleep(10)

def download_batch_results(result_file_id, output_file="batch_results.jsonl"):
    """
    Downloads the batch processing results and saves to a file.
    """
    response = client.files.content(result_file_id)
    with open(output_file, "wb") as f:
        f.write(response)
    return output_file

def parse_results_to_dataframe(result_file):
    """
    Parses the JSONL results file into a pandas DataFrame.
    """
    results = []
    with open(result_file, "r") as file:
        for line in file:
            results.append(json.loads(line))

    df = pd.DataFrame(results)
    return df

def process_batches(file_id, batch_size=10):
    """
    Processes abstracts in batches manually by splitting input data into chunks.
    """
    # Load the JSONL data
    with open(file_id, "r") as file:
        data = [json.loads(line) for line in file]

    # Break the data into chunks
    results = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        prompts = [entry["prompt"] for entry in batch]

        # Send the batch to OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Act as an expert and analyze the following prompts."},
                {"role": "user", "content": "\n\n".join(prompts)}
            ]
        )

        # Process and store the results
        for choice in response.choices:
            results.append(choice.message.content)

    return results


# Main Execution
if __name__ == "__main__":
    # Step 1: Fetch publications for an SDG
    with Session() as session:
        sdg_number = 1
        publications = fetch_publications_by_sdg(session, sdg_number)

    if not publications:
        print("No publications found for the specified SDG.")
        exit()

    # Step 2: Create JSONL file
    jsonl_file_name = "sdg_requests.jsonl"
    create_jsonl_file(jsonl_file_name, publications)
    print(f"JSONL file '{jsonl_file_name}' created.")

    # Step 3: Upload JSONL file
    file_id = upload_jsonl_file(jsonl_file_name)
    print(f"File uploaded with ID: {file_id}")

    # Step 4: Process the file in batches
    results = process_batches(jsonl_file_name, batch_size=10)

    # Step 5: Save results to a CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv("batch_results.csv", index=False)
    print("Results saved to 'batch_results.csv'.")

