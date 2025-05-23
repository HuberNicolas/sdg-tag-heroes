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

class SDGSkillsStrategy(PromptStrategy):
    """Strategy for proposing an SDG based on skills."""

    def __init__(self):
        self.context = (
            "You are a helpful assistant that proposes the most relevant Sustainable Development Goal (SDG) "
            "based on the user's skills. Be precise and provide clear reasoning."
        )

    def generate_prompt(self, skills: str) -> dict:
        return {
            "instruction": (
                "Analyze the following skills and propose the most relevant Sustainable Development Goal (SDG). "
                "Provide the id (1-17) of a single SDG and a concise reasoning for your choice. "
                "Your answer is straightforward, easy to understand and has max 2 sentences. "
                "Your answer makes the non-sustainable expert curious and want to explore. "
                #"For transparency reasons, your answers start with a short introduction who generated the answer, somthing like: As your helpful SDG-AI assistant, I recommend..."
            ),
            "skills": skills,
        }

class SDGInterestsStrategy(PromptStrategy):
    """Strategy for proposing an SDG based on interests."""

    def __init__(self):
        self.context = (
            "You are a helpful assistant that proposes the most relevant Sustainable Development Goal (SDG) "
            "based on the user's interests. Be precise and provide clear reasoning."
        )

    def generate_prompt(self, interests: str) -> dict:
        return {
            "instruction": (
                "Analyze the following interests and propose the most relevant Sustainable Development Goal (SDG). "
                "Provide the id (1-17) of a single SDG and a concise reasoning for your choice."
                "Your answer is straightforward, easy to understand and has max 2 sentences. "
                "Your answer makes the non-sustainable expert curious and want to explore. "
                #"For transparency reasons, your answers start with a short introduction who generated the answer, somthing like: As your helpful SDG-AI assistant, I recommend..."
            ),
            "interests": interests,
        }
