from .base_strategy import PromptStrategy
import random

class GenerateCommentStrategy(PromptStrategy):
    """Strategy for generating user comments based on persona, trust score, and abstract relevance."""

    def __init__(self):
        self.context = (
            "You are an AI assistant helping users generate ultra-concise comments for scientific publications. "
            "Your responses must be short, direct, and free from unnecessary phrases like 'This study...' or 'The authors found...'. "
            "Choose the most relevant passage from the abstract based on the user's persona and focus. "
            "Ensure comments are information-dense, realistic, and varied. Adjust tone and depth based on expertise level."
        )

    def generate_prompt(self, abstract: str, persona: str, interest: str, skill: str, trust_score: float) -> dict:
        """
        Generates a GPT-based annotation prompt based on persona traits, expertise level, and a relevant passage.

        Parameters:
            abstract (str): The scientific abstract to be annotated.
            persona (str): User's Bartle persona (Achiever, Explorer, Socializer, Killer).
            interest (str): The user's interest related to the topic.
            skill (str): The user's profession/skillset.
            trust_score (float): A trust-based score (0-1) reflecting user expertise.

        Returns:
            dict: The formatted prompt for GPT processing.
        """

        # Define persona-driven analysis focus
        persona_styles = {
            "Achiever": "prioritizes measurable impact, scalability, and efficiency.",
            "Explorer": "seeks knowledge gaps, unexpected applications, and theoretical extensions.",
            "Socializer": "focuses on community relevance, ethical considerations, and discussion potential.",
            "Killer": "challenges assumptions, identifies flaws, and questions methodological validity."
        }

        # Define expertise-based response tone
        expertise_styles = {
            "Expert": "Provide a technical, high-depth response with precise terminology.",
            "Intermediate": "Provide a balanced and well-structured insight.",
            "Basic": "Provide a clear and simple observation, avoiding complex analysis."
        }

        # Assign expertise level based on trust score
        expertise_level = (
            "Expert" if trust_score > 0.7 else
            "Intermediate" if trust_score > 0.4 else
            "Basic"
        )

        return {
            "instruction": (
                f"You are analyzing the following abstract. Identify the most relevant passage for a user with a '{persona}' persona, "
                f"who {persona_styles.get(persona, 'provides an insightful annotation')}. "
                f"Then, generate a concise, information-dense annotation (max 2 sentences) that aligns with their expertise level. "
                f"{expertise_styles.get(expertise_level, 'Provide a concise and relevant response.')}"
            ),
            "abstract": abstract,
            "persona": persona,
            "interest": interest,
            "skill": skill,
            "trust_score": trust_score
        }


class GenerateAnnotationStrategy(PromptStrategy):
    """Strategy for generating annotations that consider both user label comments and decision comments."""

    def __init__(self):
        self.context = (
            "You are an AI assistant generating concise, insightful annotations for scientific publications. "
            "Your task is to synthesize relevant information based on the publication abstract, user label comments, "
            "and decision comments. Ensure that annotations are context-aware, information-dense, and aligned with the "
            "user’s persona and expertise level."
        )

    def generate_prompt(
            self, abstract: str, persona: str, interest: str, skill: str, trust_score: float,
            user_label_comment: str = None, decision_comment: str = None
    ) -> dict:
        """
        Generates a structured prompt for annotation generation.

        Parameters:
            abstract (str): The publication abstract.
            persona (str): The user's persona (Achiever, Explorer, Socializer, Killer).
            interest (str): The user's area of interest.
            skill (str): The user's skill level or profession.
            trust_score (float): User expertise score (0-1).
            user_label_comment (str, optional): The comment provided by the user label.
            decision_comment (str, optional): The consensus decision comment.

        Returns:
            dict: The structured prompt for GPT processing.
        """
        persona_styles = {
            "Achiever": "prioritizes measurable impact, scalability, and efficiency.",
            "Explorer": "seeks knowledge gaps, unexpected applications, and theoretical extensions.",
            "Socializer": "focuses on community relevance, ethical considerations, and discussion potential.",
            "Killer": "challenges assumptions, identifies flaws, and questions methodological validity."
        }

        expertise_styles = {
            "Expert": "Provide a technical, high-depth response with precise terminology.",
            "Intermediate": "Provide a balanced and well-structured insight.",
            "Basic": "Provide a clear and simple observation, avoiding complex analysis."
        }

        expertise_level = (
            "Expert" if trust_score > 0.7 else
            "Intermediate" if trust_score > 0.4 else
            "Basic"
        )

        prompt_text = (
            f"Analyze the following abstract and relevant context. Identify the key takeaways for a user with a '{persona}' persona, "
            f"who {persona_styles.get(persona, 'provides an insightful annotation')}. Generate a concise, information-dense annotation "
            f"(max 2 sentences) that aligns with their expertise level. {expertise_styles.get(expertise_level, 'Provide a concise and relevant response.')}\n\n"
            f"Abstract: {abstract}\n"
        )

        if user_label_comment:
            prompt_text += f"User Comment: {user_label_comment}\n"

        if decision_comment:
            prompt_text += f"Decision Comment: {decision_comment}\n"

        return {
            "instruction": prompt_text,
            "abstract": abstract,
            "persona": persona,
            "interest": interest,
            "skill": skill,
            "trust_score": trust_score,
            "user_label_comment": user_label_comment,
            "decision_comment": decision_comment
        }
