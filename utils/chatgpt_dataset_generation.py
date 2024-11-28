import time
from typing import Literal
import pandas as pd
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from db.mariadb_connector import engine as mariadb_engine

from datetime import datetime
from zoneinfo import ZoneInfo

from models import SDGLabelSummary
from models.sdg_prediction import SDGPrediction
from models.publications.publication import Publication
from utils.logger import logger
logging = logger("chatGPT_dataset_generator.log")



from enum import Enum
import json

import requests
from openai import OpenAI
from pydantic import BaseModel, Field

from settings.settings import ExplainerSettings
from utils.env_loader import load_env, get_env_variable


# Load the API environment variables
load_env('api.env')


# Initialize session
Session = sessionmaker(bind=mariadb_engine)


sdg_columns = [f"sdg{i}" for i in range(1, 18)]  # SDG1 to SDG17



def fetch_publications_by_sdg(session, sdg_number):
    """
    Fetches all publications for a specific SDG goal where the label summary
    has a value of 1 for the given SDG, and filters the predictions
    to include only those with the prediction_model = 'Aurora'.

    :param session: SQLAlchemy session
    :param sdg_number: SDG goal number (1-17)
    :return: List of publications with filtered SDG predictions
    """
    if not 1 <= sdg_number <= 17:
        raise ValueError("SDG number must be between 1 and 17")

    sdg_field = f"sdg{sdg_number}"

    # Dynamically filter SDGLabelSummary for the given SDG field
    sdg_label_summaries = (
        session.query(SDGLabelSummary)
        .filter(getattr(SDGLabelSummary, sdg_field) == 1)
        .options(
            joinedload(SDGLabelSummary.publication).joinedload(Publication.sdg_predictions)
        )
        .all()
    )

    results = []
    for label_summary in sdg_label_summaries:
        publication = label_summary.publication
        # Filter publication's SDG predictions for "Aurora"
        aurora_predictions = [
            prediction for prediction in publication.sdg_predictions
            if prediction.prediction_model == "Aurora"
        ]
        if aurora_predictions:
            results.append({
                "publication": publication,
                "predictions": aurora_predictions
            })

    return results

no_samples = 1
results = []

# Initialize OpenAI client (ensure you've set up the API key in your environment)
client = OpenAI()


def evaluate_abstract_sdg_relevance(abstract_text):
    """
    Calls OpenAI API to evaluate SDG relevance and confidence for the given abstract
    and enforces a structured JSON response format.

    :param abstract_text: Abstract to analyze
    :return: Dictionary with 'sdg_relevance' and 'sdg_relevance_confidence'
    """
    messages = [
        {
            "role": "system",
            "content": """
            You are an expert in sustainability, tasked with analyzing scientific abstracts based on the UN's 17 Sustainable Development Goals (SDGs).
            Always respond in the following JSON format:
            {"sdg_relevance": [float], "sdg_relevance_confidence": [float]}
            Each array must contain exactly 17 elements, where the index corresponds to the SDG number (e.g., index 0 is SDG 1, index 16 is SDG 17).
            The numbers must be between 0 and 1.
            """,
        },
        {
            "role": "user",
            "content": (
                f"Analyze the following abstract and provide the relevance and confidence values for each SDG:\n\n{abstract_text}"
            ),
        },
    ]

    # Enforce a structured JSON response format
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},  # Ensures the response is a valid JSON object
    )

    try:
        # Access and return the JSON response
        response_content = response.choices[0].message.content
        return json.loads(response_content)
    except (AttributeError, json.JSONDecodeError) as e:
        print("Error parsing the response:", e)
        print("Full response:", response)
        return None


def evaluate_abstract_for_specific_sdg(abstract_text, sdg_number):
    """
    Calls OpenAI API to evaluate the relevance and contribution of an abstract to a specific SDG
    and enforces a structured JSON response format.

    :param abstract_text: Abstract to analyze
    :param sdg_number: SDG number to evaluate (1–17)
    :return: Dictionary with arguments and scores for relevance and contribution to the specified SDG
    """
    if not 1 <= sdg_number <= 17:
        raise ValueError("SDG number must be between 1 and 17")

    messages = [
        {
            "role": "system",
            "content": """
            You are an expert in sustainability tasked with evaluating scientific abstracts based on a specific Sustainable Development Goal (SDG).
            Always respond in the following JSON format:
            {
              "arguments_for_relatedness": "string",
              "arguments_against_relatedness": "string",
              "relatedness_score": number,
              "arguments_for_contribution": "string",
              "arguments_against_contribution": "string",
              "contribution_score": number
            }
            Ensure the arguments are concise and evidence-based, and the scores are between 0 and 1.
            """,
        },
        {
            "role": "user",
            "content": f"""
            Analyze the following abstract for relevance and contribution to SDG {sdg_number}:

            {abstract_text}
            """,
        },
    ]

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},  # Ensures the response is a valid JSON object
    )

    try:
        # Access and return the JSON response
        response_content = response.choices[0].message.content
        return json.loads(response_content)
    except (AttributeError, json.JSONDecodeError) as e:
        print("Error parsing the response:", e)
        print("Full response:", response)
        return None


# Initialize an empty DataFrame to store the results
columns = [
    "publication_title",
    "publication_sql_id",
    "publication_zora_id",
    "publication_abstract",
    "prediction_model",
    "sdg",
]
# Add prediction SDG values and analysis results (relevance and confidence for all 17 SDGs)
columns += [f"prediction_sdg{i}" for i in range(1, 18)]
columns += [f"sdg_relevance_{i}" for i in range(1, 18)]
columns += [f"sdg_confidence_{i}" for i in range(1, 18)]

columns += [
    "arguments_for_relatedness",
    "arguments_against_relatedness",
    "relatedness_score",
    "arguments_for_contribution",
    "arguments_against_contribution",
    "contribution_score",
]

results_df = pd.DataFrame(columns=columns)

with (Session() as session):
    for sdg in range(1, 18):
        print(f"Fetching publications for SDG {sdg}...")
        start = time.time()
        publications_data = fetch_publications_by_sdg(session, sdg)
        end = time.time()
        for data in publications_data:
            publication = data["publication"]
            # predictions = data["predictions"]
            #print(f"Publication ID: {data['publication'].publication_id}, Title: {data['publication'].title}")

            # TO BE ADDED TO DF
            publication_title = publication.title
            publication_sql_id = publication.publication_id
            publication_zora_id = publication.oai_identifier
            publication_abstract = publication.description

            predictions = data["predictions"][0]
            prediction_model = predictions.prediction_model
            #print(predictions.sdg1)
            # Extract prediction SDG values
            prediction_scores = {f"prediction_sdg{i}": getattr(predictions, f"sdg{i}", None) for i in range(1, 18)}


            # Generate 17 predictions values
            analysis_result = evaluate_abstract_sdg_relevance(publication.description)
            if analysis_result:
                # ADD 17 sdg_relevance values
                sdg_relevance = analysis_result.get("sdg_relevance", [None] * 17)
                # ADD 17 sdg_confidence values
                sdg_confidence = analysis_result.get("sdg_relevance_confidence", [None] * 17)
                print("SDG Relevance:", sdg_relevance)
                print("SDG Confidence:", sdg_confidence)
            else:
                sdg_relevance = [None] * 17
                sdg_confidence = [None] * 17
                print("Failed to analyze the abstract.")

            # Evaluate the abstract for the specified SDG
            evaluation_result = evaluate_abstract_for_specific_sdg(publication.description, sdg)

            # Display the result
            if evaluation_result:
                arguments_for_relatedness = evaluation_result.get("arguments_for_relatedness", "")
                arguments_against_relatedness = evaluation_result.get("arguments_against_relatedness", "")
                relatedness_score = evaluation_result.get("relatedness_score", None)

                arguments_for_contribution = evaluation_result.get("arguments_for_contribution", "")
                arguments_against_contribution = evaluation_result.get("arguments_against_contribution", "")
                contribution_score = evaluation_result.get("contribution_score", None)
            else:
                arguments_for_relatedness = ""
                arguments_against_relatedness = ""
                relatedness_score = None

                arguments_for_contribution = ""
                arguments_against_contribution = ""
                contribution_score = None

            # Append data to the DataFrame
            row_data = {
                "publication_title": publication_title,
                "publication_sql_id": publication_sql_id,
                "publication_zora_id": publication_zora_id,
                "publication_abstract": publication_abstract,
                "prediction_model": prediction_model,
                "sdg": sdg,
                "arguments_for_relatedness": arguments_for_relatedness,
                "arguments_against_relatedness": arguments_against_relatedness,
                "relatedness_score": relatedness_score,
                "arguments_for_contribution": arguments_for_contribution,
                "arguments_against_contribution": arguments_against_contribution,
                "contribution_score": contribution_score,
            }
            row_data.update({f"sdg_relevance_{i + 1}": sdg_relevance[i] for i in range(17)})
            row_data.update({f"sdg_confidence_{i + 1}": sdg_confidence[i] for i in range(17)})
            row_data.update(prediction_scores)

            results_df = pd.concat(
                [results_df, pd.DataFrame([row_data])],
                ignore_index=True
            )
            break
        #break



# Save the DataFrame to a CSV file
results_df.to_csv("sdg_evaluation_results.csv", index=False)
print("Results saved to sdg_evaluation_results.csv")

