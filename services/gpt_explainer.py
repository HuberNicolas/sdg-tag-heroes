import json
from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI
import instructor
from settings.settings import ExplainerSettings
from utils.env_loader import load_env, get_env_variable

# Load the API environment variables
load_env('api.env')

explainer_settings = ExplainerSettings()
client = instructor.from_openai(OpenAI(api_key=get_env_variable('OPENAI_API_KEY')))
MODEL = "gpt-4o-2024-08-06"
#MODEL = "gpt-3.5-turbo"


class PromptStrategy:
    """Base class for prompt strategies."""

    def generate_prompt(self, title: str, abstract: str):
        raise NotImplementedError("Subclasses must implement this method.")


class ExtractKeywordsStrategy(PromptStrategy):
    """Extracts keywords from an abstract."""

    def generate_prompt(self, title: str, abstract: str):
        return {
            "instruction": "Extract exactly 4 keywords that represent the main topics of the abstract.",
            "title": title,
            "abstract": abstract
        }

class SummarizePublicationStrategy(PromptStrategy):
    """Summarizes a publication with maximum information density for non-experts."""

    def generate_prompt(self, title: str, abstract: str):
        return {
            "instruction": (
                "Summarize the publication in one sentence with the highest possible information density, "
                "making it understandable and engaging for non-experts."
            ),
            "title": title,
            "abstract": abstract
        }


class TargetStrategy(PromptStrategy):
    """Evaluates relevance to a specific UN SDG target."""

    def __init__(self, target: str):
        self.target = target

    def generate_prompt(self, title: str, abstract: str):
        return {
            "instruction": f"Evaluate the abstract's relevance to UN SDG Target {self.target}. Provide reasoning for and against relevance.",
            "title": title,
            "abstract": abstract
        }


class GoalStrategy(PromptStrategy):
    """Evaluates relevance to a specific UN SDG goal."""

    def __init__(self, goal: str):
        self.goal = goal

    def generate_prompt(self, title: str, abstract: str):
        return {
            "instruction": f"Evaluate the abstract's relevance to UN SDG Goal {self.goal}. Provide reasoning for and against relevance.",
            "title": title,
            "abstract": abstract
        }

class FactStrategy(PromptStrategy):
    """Generates a 'Did-You-Know' fact from an abstract."""

    def generate_prompt(self, title: str, abstract: str):
        return {
            "instruction": (
                "Create a single, catchy, and engaging sentence that summarizes this scientific abstract's key "
                "finding or idea. It should be accessible to a general audience and highlight the study's most "
                "interesting or surprising aspect."
            ),
            "title": title,
            "abstract": abstract
        }

# Pydantic response models

class SDGAnalysisResponse(BaseModel):
    reasoning_for: str = Field(description="Reasoning for why the SDG prediction aligns with the abstract.")
    reasoning_against: str = Field(description="Reasoning against why the SDG prediction aligns with the abstract.")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0.")

class KeywordResponse(BaseModel):
    keywords: list[str] = Field(description="The list of extracted keywords.")

class FactResponse(BaseModel):
    fact: str

class SummaryResponse(BaseModel):
    summary: str


class SDGExplainer:
    """Main SDG Explainer class using Instructor library and function calling."""

    def __init__(self):
        self.context = "You are an expert in sustainability research providing structured JSON answers."

    def _call_model(self, prompt_data: dict, response_model):
        """Handles the API call with the Instructor client."""
        response = client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.context},
                {"role": "user", "content": json.dumps(prompt_data)}
            ],
            response_format=response_model,
        )
        return response.choices[0].message.parsed

    def extract_keywords(self, title: str, abstract: str) -> list[str]:
        """Extracts keywords using the ExtractKeywordsStrategy."""
        strategy = ExtractKeywordsStrategy()
        prompt_data = strategy.generate_prompt(title, abstract)
        response = self._call_model(prompt_data, KeywordResponse)
        return response.keywords

    def analyze_sdg(self, title: str, abstract: str, goal: str = None, target: str = None) -> SDGAnalysisResponse:
        """Analyzes SDG relevance based on the provided goal or target."""
        if target:
            strategy = TargetStrategy(target)
        elif goal:
            strategy = GoalStrategy(goal)
        else:
            raise ValueError("Either 'goal' or 'target' must be specified.")

        prompt_data = strategy.generate_prompt(title, abstract)
        return self._call_model(prompt_data, SDGAnalysisResponse)

    def create_fact(self, title: str, abstract: str) -> str:
        """Generates a 'Did-You-Know' fact using the FactStrategy."""
        strategy = FactStrategy()
        prompt_data = strategy.generate_prompt(title, abstract)
        response = self._call_model(prompt_data, FactResponse)
        return response.fact

    def summarize_publication(self, title: str, abstract: str) -> str:
        """
        Summarizes a publication using the SummarizePublicationStrategy.

        Args:
            title (str): The title of the publication.
            abstract (str): The abstract of the publication.

        Returns:
            str: A concise summary of the publication.
        """
        strategy = SummarizePublicationStrategy()
        prompt_data = strategy.generate_prompt(title, abstract)
        response = self._call_model(prompt_data, SummaryResponse)
        return response.summary

