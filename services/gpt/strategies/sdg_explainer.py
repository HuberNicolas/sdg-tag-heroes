from .strategy import PromptStrategy

class TargetStrategy(PromptStrategy):

    """Analyzes SDG relevance based on the provided target."""

    def __init__(self, target: str):
        self.target = target
        self.context = "You are an expert in sustainable development goals (SDGs). Analyze relevance to specific targets."

    def generate_prompt(self, title: str, abstract: str) -> dict:
        return {
            "instruction": f"Evaluate the abstract's relevance to UN SDG Target {self.target}. Provide reasoning for and against relevance.",
            "title": title,
            "abstract": abstract
        }

class GoalStrategy(PromptStrategy):

    """Analyzes SDG relevance based on the provided goal."""

    def __init__(self, goal: str):
        self.goal = goal
        self.context = "You are an expert in sustainable development goals (SDGs). Analyze relevance to specific goals."

    def generate_prompt(self, title: str, abstract: str) -> dict:
        return {
            "instruction": f"Evaluate the abstract's relevance to UN SDG Goal {self.goal}. Provide reasoning for and against relevance.",
            "title": title,
            "abstract": abstract
        }
