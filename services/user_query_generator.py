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

from pydantic import BaseModel, Field

class SkillsQueryResponse(BaseModel):
    skills: str = Field(description="The input description of the user's skills.")
    generated_query: str = Field(description="The User description generated based on the user's skills.")

class InterestsQueryResponse(BaseModel):
    interests: str = Field(description="The input description of the user's interests.")
    generated_query: str = Field(description="The User description generated based on the user's interests.")

class UserQueryGenerator:
    """Generates enriched user descriptions based on skills or interests for finding relevant scientific publications."""

    def __init__(self):
        self.context = (
            "You are a helpful assistant that enriches user inputs into detailed and engaging descriptions "
            "to help them find relevant scientific publications. Be creative and informative."
        )

    def _call_model(self, prompt_data: dict, response_model):
        """
        Handles the API call with the Instructor client.

        Args:
            prompt_data (dict): The prompt data for the model.
            response_model (BaseModel): The Pydantic model to validate the response.

        Returns:
            BaseModel: The validated response parsed into the specified Pydantic model.
        """
        response = client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.context},
                {"role": "user", "content": json.dumps(prompt_data)}
            ],
            response_format=response_model,
        )
        return response.choices[0].message.parsed

    def generate_skills_description(self, skills: str) -> SkillsQueryResponse:
        """
        Generates an enriched description based on the user's skills or profession.

        Args:
            skills (str): A description of the user's skills, background, or expertise.

        Returns:
            SkillsQueryResponse: The response containing the skills and the enriched description.
        """
        prompt_data = {
            "instruction": (
                "Enrich the following user-provided skills or professional background into a detailed, engaging description. "
                "Focus on highlighting the user's expertise in an interesting and contextually rich manner, suitable for finding "
                "relevant scientific publications."
            ),
            "skills": skills,
        }
        return self._call_model(prompt_data, SkillsQueryResponse)

    def generate_interests_description(self, interests: str) -> InterestsQueryResponse:
        """
        Generates an enriched description based on the user's interests or aspirations.

        Args:
            interests (str): A description of the user's interests or topics they want to learn about.

        Returns:
            InterestsQueryResponse: The response containing the interests and the enriched description.
        """
        prompt_data = {
            "instruction": (
                "Enrich the following user-provided interests or aspirations into a detailed, engaging description. "
                "Focus on making the interests exciting, imaginative, and contextually rich, suitable for finding "
                "relevant scientific publications."
            ),
            "interests": interests,
        }
        return self._call_model(prompt_data, InterestsQueryResponse)

