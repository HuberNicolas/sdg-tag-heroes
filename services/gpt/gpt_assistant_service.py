import json
from typing import List, Optional, Dict, Any

import instructor
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from sympy.physics.units import temperature

from enums import SDGType
from schemas.gpt_assistant_service import GPTResponseKeywordsSchema, GPTResponseSDGAnalysisSchema, \
    GPTResponseFactSchema, GPTResponseSummarySchema, GPTResponseCollectiveSummarySchema, GPTResponseSkillsQuerySchema, \
    GPTResponseAnnotationScoreSchema, GPTResponseCommentSummarySchema, SDGPredictionSchema, \
    GPTPersonaResponseAnnotationSchema, GPTPersonaResponseCommentSchema
from settings.settings import GPTAssistantServiceSettings
from utils.env_loader import load_env, get_env_variable
from .strategies.fact_generator_strategy import FactStrategy
from .strategies.keyword_extractor_strategy import ExtractKeywordsStrategy
from .strategies.persona_comment_generator_strategy import GenerateCommentStrategy, GenerateAnnotationStrategy
from .strategies.sdg_explainer_strategy import GoalStrategy, TargetStrategy
from .strategies.summarize_sdg_user_label_comments import SummarizeSDGUserLabelCommentsStrategy
from .strategies.summarizer_strategy import SummarizeSinglePublicationStrategy, SummarizeMultiplePublicationsStrategy
from .strategies.user_annotation_evaluator_strategy import AnnotationEvaluatorStrategy
from .strategies.user_query_generator_strategy import SkillsQueryStrategy, InterestsQueryStrategy, SDGSkillsStrategy, \
    SDGInterestsStrategy

# Load the API environment variables
load_env('api.env')

gpt_assistant_service_settings = GPTAssistantServiceSettings()
client = instructor.from_openai(OpenAI(api_key=get_env_variable('OPENAI_API_KEY')))


class GPTAssistantService:
    """General-purpose GPT client for structured API calls with contextual prompts."""

    def __init__(self, client: Any=client, model: str=gpt_assistant_service_settings.GPT_MODEL):
        self.client = client
        self.model = model

    def _call_model(self, context: str, prompt_data: dict, response_model: type[BaseModel]):
        """Handles the API call with contextual prompts."""
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": json.dumps(prompt_data)}
                ],
                temperature=0.7,
                response_format=response_model
            )
            return response.choices[0].message.parsed
        except ValidationError as e:
            raise ValueError(f"Invalid response format: {str(e)}")

    def _call_creative_model(self, context: str, prompt_data: dict, response_model: type[BaseModel]):
        """Handles the API call with contextual prompts."""
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": json.dumps(prompt_data)}
                ],
                temperature=1.2,  # Set temperature (0.7-1.5 recommended for high creativity)
                response_format=response_model
            )
            return response.choices[0].message.parsed
        except ValidationError as e:
            raise ValueError(f"Invalid response format: {str(e)}")

    def extract_keywords(self, title: str, abstract: str) -> GPTResponseKeywordsSchema:
        """Extracts keywords with a context specific to keyword extraction."""
        strategy = ExtractKeywordsStrategy()
        prompt_data = strategy.generate_prompt(title, abstract)
        response = self._call_model(strategy.context, prompt_data, GPTResponseKeywordsSchema)
        return response.keywords

    def analyze_sdg(self, title: str, abstract: str, goal: Optional[str] = None, target: Optional[str] = None) -> GPTResponseSDGAnalysisSchema:
        """Analyzes SDG relevance using the provided goal or target."""
        if target:
            strategy = TargetStrategy(target)
        elif goal:
            strategy = GoalStrategy(goal)
        else:
            raise ValueError("Either 'goal' or 'target' must be specified.")

        prompt_data = strategy.generate_prompt(title, abstract)
        return self._call_model(strategy.context, prompt_data, GPTResponseSDGAnalysisSchema)

    def create_fact(self, title: str, abstract: str) -> GPTResponseFactSchema:
        """Generates a 'Did-You-Know' fact from the provided data."""
        strategy = FactStrategy()
        prompt_data = strategy.generate_prompt(title, abstract)
        response = self._call_model(strategy.context, prompt_data, GPTResponseFactSchema)
        return response.fact

    def summarize_publication(self, title: str, abstract: str) -> GPTResponseSummarySchema:
        """Summarizes a publication into a concise summary."""
        strategy = SummarizeSinglePublicationStrategy()
        prompt_data = strategy.generate_prompt(title, abstract)
        response = self._call_model(strategy.context, prompt_data, GPTResponseSummarySchema)
        return response.summary

    def summarize_publications(self, publications: List[Dict[str, str]]) -> GPTResponseCollectiveSummarySchema:
        """Summarizes a set of publications into a single summary and extracts keywords."""
        strategy = SummarizeMultiplePublicationsStrategy()
        prompt_data = strategy.generate_prompt(publications)

        try:
            response = self._call_model(strategy.context, prompt_data, GPTResponseCollectiveSummarySchema)
            return response
        except Exception as e:
            return GPTResponseCollectiveSummarySchema(
                summary=f"Error generating summary: {str(e)}",
                keywords=[]
            )

    def summarize_comments(self, user_labels: List[Dict[str, str]]) -> GPTResponseCommentSummarySchema:
        """Summarizes a set comments form sdg_user_labels into a single comment."""
        strategy = SummarizeSDGUserLabelCommentsStrategy()
        prompt_data = strategy.generate_prompt(user_labels)

        try:
            response = self._call_model(strategy.context, prompt_data, GPTResponseCommentSummarySchema)
            return response
        except Exception as e:
            return GPTResponseCollectiveSummarySchema(
                summary=f"Error generating summary: {str(e)}",
                keywords=[]
            )

    def generate_skills_description(self, skills: str) -> GPTResponseSkillsQuerySchema:
        """Generates an enriched description for the user's skills."""
        strategy = SkillsQueryStrategy()
        prompt_data = strategy.generate_prompt(skills)
        return self._call_model(strategy.context, prompt_data, GPTResponseSkillsQuerySchema)

    def generate_interests_description(self, interests: str) -> GPTResponseSkillsQuerySchema:
        """Generates an enriched description for the user's interests."""
        strategy = InterestsQueryStrategy()
        prompt_data = strategy.generate_prompt(interests)
        return self._call_model(strategy.context, prompt_data, GPTResponseSkillsQuerySchema)

    def propose_sdg_from_skills(self, skills: str) -> SDGPredictionSchema:
        """Propose the most suitable SDG based on the user's skills."""
        strategy = SDGSkillsStrategy()
        prompt_data = strategy.generate_prompt(skills)
        return self._call_model(strategy.context, prompt_data, SDGPredictionSchema)

    def propose_sdg_from_interests(self, interests: str) -> SDGPredictionSchema:
        """Propose the most suitable SDG based on the user's interests."""
        strategy = SDGInterestsStrategy()
        prompt_data = strategy.generate_prompt(interests)
        return self._call_model(strategy.context, prompt_data, SDGPredictionSchema)


    def evaluate_annotation(self, passage: str, annotation: str, sdg_label: SDGType) -> GPTResponseAnnotationScoreSchema:
        """Evaluates user annotations based on relevance, depth, correctness, and creativity."""
        strategy = AnnotationEvaluatorStrategy()
        prompt_data = strategy.generate_prompt(passage, annotation, sdg_label)
        response = self._call_model(strategy.context, prompt_data, GPTResponseAnnotationScoreSchema)
        return response

    def generate_comment(self, abstract: str, persona: str, interest: str, skill: str,
                            trust_score: float) -> GPTPersonaResponseCommentSchema:
        """Generates a comment tailored to the user's persona and expertise level."""
        strategy = GenerateCommentStrategy()
        prompt_data = strategy.generate_prompt(abstract, persona, interest, skill, trust_score)
        response = self._call_creative_model(strategy.context, prompt_data, GPTPersonaResponseCommentSchema)
        return response

    def generate_annotation(
            self, abstract: str, persona: str, interest: str, skill: str, trust_score: float,
            user_label_comment: str = None, decision_comment: str = None
    ) -> GPTPersonaResponseAnnotationSchema:
        """
        Generates an annotation based on the structured prompt.

        Parameters:
            abstract (str): The publication abstract.
            persona (str): The user's persona (Achiever, Explorer, Socializer, Killer).
            interest (str): The user's interest in the topic.
            skill (str): The user's skill level or profession.
            trust_score (float): The user’s expertise score (0-1).
            user_label_comment (str, optional): The comment from the user label.
            decision_comment (str, optional): The consensus decision comment.

        Returns:
            str: A concise and relevant annotation.
        """
        strategy = GenerateAnnotationStrategy()
        prompt_data = strategy.generate_prompt(
            abstract, persona, interest, skill, trust_score, user_label_comment, decision_comment
        )

        response = self._call_creative_model(strategy.context, prompt_data, GPTPersonaResponseAnnotationSchema)
        return response
