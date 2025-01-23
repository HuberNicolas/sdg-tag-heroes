from .base_strategy import PromptStrategy


class SkillsQueryStrategy(PromptStrategy):
    """Strategy for generating enriched user descriptions based on skills."""

    def __init__(self):
        self.context = (
            "You are a helpful assistant that enriches user inputs into detailed and engaging descriptions "
            "to help them find relevant scientific publications. Be creative and informative."
        )

    def generate_prompt(self, skills: str) -> dict:
        return {
            "instruction": (
                "Enrich the following user-provided skills or professional background into a detailed, engaging description. "
                "Focus on highlighting the user's expertise in an interesting and contextually rich manner, suitable for finding "
                "relevant scientific publications."
            ),
            "skills": skills,
        }


class InterestsQueryStrategy(PromptStrategy):
    """Strategy for generating enriched user descriptions based on interests."""

    def __init__(self):
        self.context = (
            "You are a helpful assistant that enriches user inputs into detailed and engaging descriptions "
            "to help them find relevant scientific publications. Be creative and imaginative."
        )

    def generate_prompt(self, interests: str) -> dict:
        return {
            "instruction": (
                "Enrich the following user-provided interests or aspirations into a detailed, engaging description. "
                "Focus on making the interests exciting, imaginative, and contextually rich, suitable for finding "
                "relevant scientific publications."
            ),
            "interests": interests,
        }
