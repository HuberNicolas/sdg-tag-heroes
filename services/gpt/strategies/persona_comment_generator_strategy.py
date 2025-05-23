from .base_strategy import PromptStrategy
import random

class GenerateCommentStrategy(PromptStrategy):
    """Strategy for generating user comments based on persona, trust score, and abstract relevance."""

    def __init__(self):
        self.context = (
            "You are an AI assistant tasked with mimicking real human responses, providing ultra-concise comments for scientific publications. "
            "Your comments should be relevant to the abstract based on the user’s persona and expertise level. "
            "Responses must be direct, short, and free from fluff (e.g., 'This study...' or 'The authors found...'). "
            "Focus on extracting and commenting on the most relevant passage from the abstract. "
            "Style should vary with persona and expertise level, ensuring that each comment is realistic, insightful, and persona-specific."
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

        # Define persona-driven analysis focus with more nuanced approaches
        persona_styles = {
            "Achiever": "values measurable impact, scalability, and efficiency. Typically focused on outcomes that can be tracked and optimized. Could emphasize practical applications or theoretical limits, depending on user skill.",
            "Explorer": "actively seeks knowledge gaps and theoretical extensions, interested in unexpected applications and novel concepts. More likely to provide open-ended, exploratory thoughts.",
            "Socializer": "concerned with community relevance, ethical considerations, and the broader discussion potential. Can be more conversational, using accessible language while remaining scientific. Often encourages further inquiry or debates.",
            "Killer": "interested in challenging assumptions, identifying flaws, and questioning methodological validity. Likely to point out gaps, inconsistencies, or areas needing clarification. Often delivers critiques that demand attention."
        }

        # Define expertise-based response tone, with additional adjustments
        expertise_styles = {
            "Expert": "Provide a high-depth, technical response using precise terminology, but also ensure that the explanation is directly relevant to the abstract. Avoid generalizations, focus on specificity.",
            "Intermediate": "Provide a balanced, well-structured response with some technical detail, but make it approachable. The aim is for clarity and relevance without overwhelming the reader.",
            "Basic": "Provide a concise, simplified observation that stays grounded in the core points of the abstract. Avoid complexity, focusing on easily digestible ideas that do not assume deep technical knowledge."
        }

        # Assign expertise level dynamically based on trust score
        expertise_level = (
            "Expert" if trust_score > 0.9 else
            "Intermediate" if trust_score > 0.4 else
            "Basic"
        )

        # Add personality considerations for a diverse set of responses
        prompt = {
            "instruction": (
                f"You are analyzing the following abstract. Identify the most relevant passage for a user with a '{persona}' persona, "
                f"who {persona_styles.get(persona, 'provides insightful annotations based on their unique style and focus.')}. "
                f"Then, generate a concise, information-dense annotation (max 2 sentences) that aligns with their expertise level. "
                f"{expertise_styles.get(expertise_level, 'Ensure the response is clear, relevant, and approachable for the given skill level.')} "
                "Feel free to incorporate personalized insights based on the user’s persona and focus. "
                "Do not shy away from making your tone more relaxed or formal, depending on the user’s style."
            ),
            "abstract": abstract,
            "persona": persona,
            "interest": interest,
            "skill": skill,
            "trust_score": trust_score
        }
        return prompt



class GenerateAnnotationStrategy(PromptStrategy):
    """Strategy for generating annotations based on user labels and decision comments."""

    def __init__(self):
        self.context = (
            "You are an AI assistant tasked with synthesizing annotations for scientific publications. "
            "Your annotations should reflect the context of the user’s persona, expertise, and comments provided. "
            "Ensure that annotations are tailored to be relevant to the user's background and knowledge, focusing on insightful contributions."
        )

    def generate_prompt(self, abstract: str, persona: str, interest: str, skill: str, trust_score: float,
                        user_label_comment: str = None, decision_comment: str = None) -> dict:
        """
        Generates a structured prompt for annotation generation based on user labels and decision comments.

        Parameters:
            abstract (str): The publication abstract.
            persona (str): The user's persona (Achiever, Explorer, Socializer, Killer).
            interest (str): The user's interest in the topic.
            skill (str): The user's skill level or profession.
            trust_score (float): The user’s expertise score (0-1).
            user_label_comment (str, optional): The comment from the user label.
            decision_comment (str, optional): The consensus decision comment.

        Returns:
            dict: The structured prompt for GPT processing.
        """
        persona_styles = {
            "Achiever": "values measurable outcomes, focusing on practicality and efficiency. The Achiever persona will likely favor annotations with a clear, actionable takeaway.",
            "Explorer": "seeks new knowledge and theoretical perspectives. Explorers will appreciate annotations that suggest open-ended questions or novel interpretations.",
            "Socializer": "enjoys engaging discussions with ethical or community-related concerns. Annotations for Socializers can be more accessible and emphasize social impact.",
            "Killer": "prefers to critically examine assumptions and highlight flaws. Annotations for Killers should question methods, results, or gaps in the research."
        }

        expertise_styles = {
            "Expert": "Provide highly detailed and technical insights. Assume familiarity with complex terminology and focus on deep analysis.",
            "Intermediate": "Provide insights that are thorough but still digestible for those with some technical background. Keep it concise but informative.",
            "Basic": "Simplify the annotation for easy understanding. Focus on the general themes without diving into complex details or jargon."
        }

        expertise_level = (
            "Expert" if trust_score > 0.9 else
            "Intermediate" if trust_score > 0.4 else
            "Basic"
        )

        prompt_text = (
            f"Analyze the following abstract and relevant comments. Identify key takeaways for a user with a '{persona}' persona, "
            f"who {persona_styles.get(persona, 'provides insightful annotations based on their unique style and focus.')}. "
            f"Generate a concise, information-dense annotation (max 2 sentences) that aligns with their expertise level. "
            f"{expertise_styles.get(expertise_level, 'Provide a clear, relevant response without unnecessary complexity.')}\n\n"
            f"Abstract: {abstract}\n"
        )

        if user_label_comment:
            prompt_text += f"User Label Comment: {user_label_comment}\n"

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

