import time
from typing import Literal
import pandas as pd
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from db.mariadb_connector import engine as mariadb_engine

from datetime import datetime
from zoneinfo import ZoneInfo

from models.sdg_prediction import SDGPrediction
from models.publications.publication import Publication
from utils.logger import logger
logging = logger("confidence_score_chatGPT_dataset_generator.log")



from enum import Enum
import json

import requests
from openai import OpenAI
from pydantic import BaseModel, Field

from settings.settings import ExplainerSettings
from utils.env_loader import load_env, get_env_variable
import instructor

# Apply the patch to the OpenAI client
# enables response_model keyword


# Load the API environment variables
load_env('api.env')

explainer_settings = ExplainerSettings()
client = OpenAI(api_key=get_env_variable('OPENAI_API_KEY'))

MODEL = "gpt-4o-2024-08-06"
MODEL = "gpt-4o-mini-2024-07-18"
print(client)
logging.info(f"Initialized ChatGPT with model... ")

# Apply the patch to the OpenAI client
# enables response_model keyword
client = instructor.from_openai(OpenAI())
print(client)
logging.info(f"Patched ChatGPT with model... ")


# Define the initial classification prompt
initial_classification_prompt = """
Act as a sustainability expert whose goal is to label and evaluate scientific abstracts based on the Sustainable Development Goals (SDGs). You are a Harvard professor with deep expertise in sustainability, economics, and environmental science. Your language is clear, scientific, and professional. Prioritize minimal words with maximum information density.

Given a publication title and abstract, classify the abstract's content as follows:
1. Abstract information density: (High, Average, Low) – Based on the richness and detail of the abstract's information.
2. Initial SDG Guess: (0-17) – The most relevant SDG based on the content.
3. Initial SDG Guess Reasoning:
    a. Reasoning For: A concise scientific justification for why the content matches the selected SDG.
    b. Reasoning Against: A concise scientific explanation of potential limitations or aspects of the content that do not align with the selected SDG.
4. Initial SDG Guess Confidence Score: A float between 0.0 and 1.0 indicating confidence in the guess.
"""

refinement_prompt = """
Act as a sustainability expert whose goal is to refine and evaluate predictions for scientific abstracts. Your language is clear, scientific, and professional. Prioritize minimal words with maximum information density.

Given the publication's title, abstract, the current SDG goal being evaluated, and the model’s prediction score for that goal, assess the prediction as follows:
1. Model Prediction Assessment Reasoning:
    a. Reasoning For: A concise scientific explanation for why the SDG prediction aligns with the content.
    b. Reasoning Against: A concise scientific explanation for why the SDG prediction might not fully align with the content.
2. Model Prediction Confidence Score: A float between 0.0 and 1.0 indicating confidence in the refined assessment.
"""


# Example queries
initial_query = """
Title: "Advancing Renewable Energy in Sub-Saharan Africa"
Abstract: "This study explores renewable energy adoption in Sub-Saharan Africa, focusing on wind and solar energy's potential to reduce carbon emissions and improve energy access in rural areas."
"""

refinement_query = """
Title: "Advancing Renewable Energy in Sub-Saharan Africa"
Abstract: "This study explores renewable energy adoption in Sub-Saharan Africa, focusing on wind and solar energy's potential to reduce carbon emissions and improve energy access in rural areas."
Current SDG Goal: 7
Model Prediction Score: 0.92
"""


def generate_initial_query(title, abstract):
    return f"""
    Title: {title}
    Abstract: {abstract}
    """

def generate_refinement_query(title, abstract, current_sdg_goal, model_prediction_score):
    return f"""
    Title: {title}
    Abstract: {abstract}
    Current SDG Goal: {current_sdg_goal}
    Model Prediction Score: {model_prediction_score}
    """

# Define the structured output for initial classification
class InitialClassificationResponse(BaseModel):
    abstract_information_density: Literal["High", "Average", "Low"] = Field(
        description="The density of information in the abstract."
    )
    initial_sdg_guess: int = Field(
        description="The initial SDG guess, a number from 0 to 17."
    )
    initial_reasoning_for: str = Field(
        description="The reasoning for why the content matches the selected SDG."
    )
    initial_reasoning_against: str = Field(
        description="The reasoning for why the content might not fully align with the selected SDG."
    )
    initial_sdg_guess_confidence_score: float = Field(
        description="The confidence score for the initial SDG guess, between 0 and 1.",
    )


# Define the structured output for prediction refinement
class RefinementResponse(BaseModel):
    reasoning_for: str = Field(
        description="Reasoning for why the SDG prediction aligns with the content."
    )
    reasoning_against: str = Field(
        description="Reasoning for why the SDG prediction might not fully align with the content."
    )
    model_prediction_confidence_score: float = Field(
        description="Confidence score for the model's prediction assessment, between 0 and 1.",
    )


def get_initial_classification_response(query: str):
    # Simulate interaction with the model
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": initial_classification_prompt},
            {"role": "user", "content": query},
        ],
        response_format=InitialClassificationResponse,
    )
    return completion.choices[0].message.parsed


def get_refinement_response(query: str):
    # Simulate interaction with the model
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": refinement_prompt},
            {"role": "user", "content": query},
        ],
        response_format=RefinementResponse,
    )
    return completion.choices[0].message.parsed


# Initialize session
Session = sessionmaker(bind=mariadb_engine)


sdg_columns = [f"sdg{i}" for i in range(1, 18)]  # SDG1 to SDG17
print(sdg_columns)
filter_ranges = [[1.0, 0.99]]

no_samples = 1

results = []

load = True
if load:
    with (Session() as session):


        for sdg_index, sdg_column in enumerate(sdg_columns, start=1):
            print(f"Processing SDG{sdg_index}...")

            level = 1  # Start level numbering at 1 for each SDG

            for range_index, (upper, lower) in enumerate(filter_ranges, start=1):
                print(f"  Applying filter range {upper} - {lower}... - Level {level}")

                start = time.time()
                # Query publications based on SDG filter
                publications = (
                    session.query(Publication)
                    .join(SDGPrediction, Publication.publication_id == SDGPrediction.publication_id)
                    .options(joinedload(Publication.sdg_predictions))
                    .filter(
                        SDGPrediction.prediction_model == "Aurora",
                        getattr(SDGPrediction, sdg_column) <= upper,
                        getattr(SDGPrediction, sdg_column) > lower,
                    )
                    .order_by(getattr(SDGPrediction, sdg_column).desc())
                    .all()

                )
                end = time.time()

                logging.info(
                    f"  Found {len(publications)} publications for SDG{sdg_index} in range {upper} - {lower}. Took {end - start} seconds."
                )

                if publications:
                    # Always log and print details of the first candidate
                    first_candidate = publications[0]  # Access the first publication
                    model_prediction = getattr(first_candidate.sdg_predictions[0], sdg_column)  # Dynamic SDG value
                    logging.info(
                        f"  First Example for SDG{sdg_index}: Title: '{first_candidate.title}', Model Prediction Score: {model_prediction}"
                    )
                    print(
                        f"SDG{sdg_index}: Title: '{first_candidate.title}', Model Prediction Score: {model_prediction}"
                    )

                if not publications:
                    continue  # Skip if no publications for this SDG and range

                # Select top candidates and log their model values
                candidates = publications[:no_samples]
                logging.info(
                    f" Selected Top {no_samples}: {[candidate.publication_id for candidate in candidates]}"
                )

                logging.info(
                    f"  Selected Top {len(candidates)} for SDG{sdg_index}: "
                    f"{', '.join([f'({candidate.publication_id}, {candidate.title.split()[0]} ... {candidate.title.split()[-1]}, {getattr(candidate.sdg_predictions[0], sdg_column):.4f})' for candidate in candidates])}"
                )

                for publication in candidates:
                    publication_id = publication.publication_id
                    title = publication.title
                    abstract = publication.description
                    oai_identifier = publication.oai_identifier
                    model_prediction = getattr(publication.sdg_predictions[0], sdg_column)

                    # Get initial classification response
                    initial_query = generate_initial_query(title, abstract)
                    logging.info(f"Initial Query: {initial_query}")
                    initial_response = get_initial_classification_response(initial_query)
                    # print(initial_response.model_dump())

                    # Extract initial classification data
                    abstract_information_density = initial_response.abstract_information_density
                    initial_sdg_guess = initial_response.initial_sdg_guess
                    initial_reasoning_for = initial_response.initial_reasoning_for
                    initial_reasoning_against = initial_response.initial_reasoning_against
                    initial_sdg_guess_confidence_score = initial_response.initial_sdg_guess_confidence_score

                    # Get refinement response
                    refinement_query = generate_refinement_query(title, abstract, sdg_index, model_prediction)
                    logging.info(f"Refinement Query: {refinement_query}")
                    refinement_response = get_refinement_response(refinement_query)
                    # print(refinement_response.model_dump())

                    # Extract refinement response data
                    model_prediction_assessment_reasoning_for = refinement_response.reasoning_for
                    model_prediction_assessment_reasoning_against = refinement_response.reasoning_against
                    model_prediction_confidence_score = refinement_response.model_prediction_confidence_score

                    timestamp = datetime.now(ZoneInfo("Europe/Zurich"))


                    # Append the extracted data to the results list
                    results.append({
                        "publication_id": publication_id,
                        "title": title,
                        "abstract": abstract,
                        "oai_identifier": oai_identifier,
                        "prediction": model_prediction,
                        "sdg": sdg_index,
                        "OUT_Q1_abstract_information_density": abstract_information_density,
                        "OUT_Q1_initial_sdg_guess": initial_sdg_guess,
                        "OUT_Q1_initial_reasoning_for": initial_reasoning_for,
                        "OUT_Q1_initial_reasoning_against": initial_reasoning_against,
                        "OUT_Q1_initial_sdg_guess_confidence_score": initial_sdg_guess_confidence_score,
                        #"initial_query": initial_query,
                        # Store query parameters instead of full query
                        #"initial_query_params": {
                            #"title": title,
                            #"abstract": abstract,
                        #},
                        "OUT_Q2_refinement_reasoning_for": model_prediction_assessment_reasoning_for,
                        "OUT_Q2_refinement_reasoning_against": model_prediction_assessment_reasoning_against,
                        "OUT_Q2_model_prediction_confidence_score": model_prediction_confidence_score,
                        #"refinement_query": refinement_query,
                        #"refinement_query_params": {
                            #"title": title,
                            #"abstract": abstract,
                            #"current_sdg_goal": sdg_index,
                            #"model_prediction_score": model_prediction,
                        #},
                        "created_at": timestamp,
                    })

# abstract information densitiy: High Average Low
# initial SDG guess: 0 - 17
# initial SDG guess reasoning: Text
# initial SDG guess confidence score: 0-1
# model prediction assessment resoning: Text
# model prediction confidence score: 0-1



# Create a DataFrame from the results
df = pd.DataFrame(results)

# Save the DataFrame to a CSV file
df.to_csv("chatgpt_sdg_classification_results.csv", index=False)
print(df.head())

# Example usage
# Get initial classification response
# initial_response = get_initial_classification_response(initial_query)
# print(initial_response.model_dump())

# Get refinement response
# refinement_response = get_refinement_response(refinement_query)
# print(refinement_response.model_dump())
