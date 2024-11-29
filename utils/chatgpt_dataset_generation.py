import time
from typing import Literal
import pandas as pd
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from tqdm import tqdm

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

#
LIMIT = 100


# Initialize session
Session = sessionmaker(bind=mariadb_engine)


sdg_columns = [f"sdg{i}" for i in range(1, 18)]  # SDG1 to SDG17


# Constants for cost calculations
COST_PER_MILLION_INPUT_TOKENS = 2.50  # $ per 1M input tokens
COST_PER_MILLION_OUTPUT_TOKENS = 10.00  # $ per 1M output tokens
TOKENS_PER_WORD_ESTIMATE = 100 / 75  # Approx. 100 tokens ~ 75 words

# Function to estimate tokens from word count
def estimate_tokens(word_count):
    return int(word_count * TOKENS_PER_WORD_ESTIMATE)

# Function to count words
def count_words(text):
    return len(text.split()) if text else 0


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
        .limit(LIMIT)
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

results = []

# Initialize OpenAI client (ensure you've set up the API key in your environment)
client = OpenAI()


def evaluate_abstract_sdg_relevance(abstract_text):
    """
    Calls OpenAI API to evaluate SDG relevance and confidence for the given abstract,
    enforces a structured JSON response format, and includes word counts for input and output.

    :param abstract_text: Abstract to analyze
    :return: Dictionary with 'sdg_relevance', 'sdg_relevance_confidence',
             and word counts for input and output.
    """

    # Count words in the abstract text (input)
    input_word_count = len(abstract_text.split())

    messages = [
        {
            "role": "system",
            "content": """
            Act as a sustainability expert whose goal is to label and evaluate scientific abstracts based on the Sustainable Development Goals (SDGs).
            Your language is clear, scientific, and professional. Prioritize minimal words with maximum information density.
            Always respond in the following JSON format:
            {"sdg_relevance": [float], "sdg_relevance_confidence": [float]}
            Each array must contain exactly 17 elements, where the index corresponds to the SDG number (e.g., index 0 is SDG 1, index 16 is SDG 17).
            The numbers must be between 0 and 1.
            """,
        },
        {
            "role": "user",
            "content": (
                f"Analyze the following abstract and provide the relevance (i.e. a score for the relevance of the text for the respective SDG) and confidence (i.e. an assessment of how sure you are about each of the scores) values for each SDG:"
                f"If you gave a high score and you are sure about it, give a confidence close to 1. If you gave a low score and you are sure that there is no relevance, give a score close to 1 as well. If you gave a high relevance score and unsure about it, give a low relevance confidence score. If you gave a low relevance score and are unsure about it, give a low relevance confidence score." 
                f"\n\n{abstract_text}"
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
        output_word_count = len(response_content.split())  # Count words in the output

        # Parse the JSON response
        parsed_response = json.loads(response_content)

        return {
            "parsed_response": parsed_response,
            "input_word_count": input_word_count,
            "output_word_count": output_word_count,
        }

    except (KeyError, json.JSONDecodeError) as e:
        print("Error parsing the response:", e)
        print("Full response:", response)
        return {
            "parsed_response": None,
            "input_word_count": input_word_count,
            "output_word_count": 0,
        }


def evaluate_abstract_for_specific_sdg(abstract_text, sdg_number):
    """
    Calls OpenAI API to evaluate SDG relevance and confidence for the given abstract,
    enforces a structured JSON response format, and includes word counts for input and output.

    :param abstract_text: Abstract to analyze
    :return: Dictionary with 'sdg_relevance', 'sdg_relevance_confidence',
             and word counts for input and output.
    """
    if not 1 <= sdg_number <= 17:
        raise ValueError("SDG number must be between 1 and 17")

    # Count words in the abstract text (input)
    input_word_count = len(abstract_text.split()) + 1 # + 1 for sdg_number

    messages = [
        {
            "role": "system",
            "content": """
            You are an expert in sustainability tasked with evaluating scientific abstracts based on a specific Sustainable Development Goal (SDG).
            To save tokens, do not always start with filling words like 'the text talks about' ... but get straight to the point, like 'there is evidence that...'
            Your language is clear, scientific, and professional. Prioritize minimal words with maximum information density.
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
                Read the following abstract and analyze its relevance to SDG {sdg_number}. 
                First, evaluate the relatedness of the given text to the SDG. In \"arguments_for_relatedness\", state why the text is related to SDG {sdg_number}. In \"arguments_against_relatedness\", state why the text is not related to SDG {sdg_number}. Finally, in \"relatedness_score\", provide a final evaluation if the text is related to SDG {sdg_number} (0 to 1). A score closer to 1 indicates high relatedness, while a score closer to 0 indicates low relatedness.
                Second, evaluate the contribution of the text to SDG {sdg_number}. Be more discriminative in this evaluation and consider if the text directly contributes to the SDG. In \"arguments_for_contribution\", state why the text directly contributes to SDG {sdg_number}. In \"arguments_against_contribution\", state why the text does not directly contribute to SDG {sdg_number}. Finally, in \"contribution_score\", provide a numerical evaluation of the contribution (0 to 1). A score closer to 1 indicates direct contribution, while a score closer to 0 indicates no direct contribution.
                Here is the abstract:
                {abstract_text}
            """
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


        output_word_count = len(response_content.split())  # Count words in the output

        # Parse the JSON response
        parsed_response = json.loads(response_content)

        return {
            "parsed_response": parsed_response,
            "input_word_count": input_word_count,
            "output_word_count": output_word_count,
        }
    except (KeyError, json.JSONDecodeError) as e:
        print("Error parsing the response:", e)
        print("Full response:", response)
        return {
            "parsed_response": None,
            "input_word_count": input_word_count,
            "output_word_count": 0,
        }


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

# Add additional columns to track word and token counts, and costs
columns += [
    "abstract_word_count", "abstract_token_count",
    "input_word_count", "input_token_count", "input_cost",
    "output_word_count", "output_token_count", "output_cost",
    "total_cost"
]

results_df = pd.DataFrame(columns=columns)

with (Session() as session):
    for sdg in range(1, 18):
        print(f"Fetching publications for SDG {sdg}...")
        start = time.time()
        publications_data = fetch_publications_by_sdg(session, sdg)
        end = time.time()
        print(f"Took {end - start} seconds to fetch a total of {len(publications_data)} publications.")
        for data in tqdm(publications_data, desc=f"Processing publications for SDG {sdg}", unit="publication"):
            publication = data["publication"]

            # Extract publication details
            publication_title = publication.title
            publication_sql_id = publication.publication_id
            publication_zora_id = publication.oai_identifier
            publication_abstract = publication.description

            # Calculate word and token counts for the abstract
            abstract_word_count = len(publication_abstract.split())
            abstract_token_count = estimate_tokens(abstract_word_count)

            # Predictions and analysis results
            predictions = data["predictions"][0]
            prediction_model = predictions.prediction_model
            prediction_scores = {f"prediction_sdg{i}": getattr(predictions, f"sdg{i}", None) for i in range(1, 18)}

            # Evaluate relevance and confidence for all 17 SDGs
            analysis_result = evaluate_abstract_sdg_relevance(publication.description)
            if analysis_result:
                parsed_response = analysis_result.get("parsed_response", {})
                sdg_relevance = parsed_response.get("sdg_relevance", [None] * 17)
                sdg_confidence = parsed_response.get("sdg_relevance_confidence", [None] * 17)
                relevance_output_word_count = count_words(json.dumps(analysis_result))
            else:
                sdg_relevance = [None] * 17
                sdg_confidence = [None] * 17
                relevance_output_text = 0

            # Evaluate the abstract for the specific SDG
            evaluation_result = evaluate_abstract_for_specific_sdg(publication.description, sdg)
            if evaluation_result:
                parsed_response = evaluation_result.get("parsed_response", {})
                arguments_for_relatedness = parsed_response.get("arguments_for_relatedness", "")
                arguments_against_relatedness = parsed_response.get("arguments_against_relatedness", "")
                relatedness_score = parsed_response.get("relatedness_score", None)
                arguments_for_contribution = parsed_response.get("arguments_for_contribution", "")
                arguments_against_contribution = parsed_response.get("arguments_against_contribution", "")
                contribution_score = parsed_response.get("contribution_score", None)

                specific_output_word_count = count_words(json.dumps(evaluation_result))
            else:
                arguments_for_relatedness = ""
                arguments_against_relatedness = ""
                relatedness_score = None
                arguments_for_contribution = ""
                arguments_against_contribution = ""
                contribution_score = None
                specific_output_text = 0

            # Total input and output word counts
            input_word_count = abstract_word_count * 2  # Two prompts for the same abstract
            output_word_count = relevance_output_word_count + specific_output_word_count

            # Calculate costs based on token counts
            input_token_count = estimate_tokens(input_word_count)
            output_token_count = estimate_tokens(output_word_count)
            input_cost = (input_token_count / 1_000_000) * COST_PER_MILLION_INPUT_TOKENS
            output_cost = (output_token_count / 1_000_000) * COST_PER_MILLION_OUTPUT_TOKENS
            total_cost = input_cost + output_cost

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
                "abstract_word_count": abstract_word_count,
                "abstract_token_count": abstract_token_count,
                "input_word_count": input_word_count,
                "input_token_count": input_token_count,
                "input_cost": input_cost,
                "output_word_count": output_word_count,
                "output_token_count": output_token_count,
                "output_cost": output_cost,
                "total_cost": total_cost,
            }
            row_data.update({f"sdg_relevance_{i + 1}": sdg_relevance[i] for i in range(17)})
            row_data.update({f"sdg_confidence_{i + 1}": sdg_confidence[i] for i in range(17)})
            row_data.update(prediction_scores)

            # Convert row_data to DataFrame
            new_row_df = pd.DataFrame([row_data])

            # Validate columns match
            if set(new_row_df.columns) != set(results_df.columns):
                missing_in_row_data = set(results_df.columns) - set(new_row_df.columns)
                missing_in_results_df = set(new_row_df.columns) - set(results_df.columns)
                raise ValueError(
                    f"Column mismatch detected.\nMissing in row_data: {missing_in_row_data}\nMissing in results_df: {missing_in_results_df}")

            # Concatenate safely with ignore_index
            results_df = pd.concat([results_df, new_row_df], ignore_index=True)

            logging.info(f"Finished publication {publication_zora_id}.")
            #break Only 1 per SDG
        #break Only SDG 1

# Save the DataFrame to a CSV file
results_df.to_csv("sdg_evaluation_results_with_costs.csv", index=False)
print("Results saved to sdg_evaluation_results_with_costs.csv")

