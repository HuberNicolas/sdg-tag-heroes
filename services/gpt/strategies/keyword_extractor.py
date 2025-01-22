from .strategy import PromptStrategy

class ExtractKeywordsStrategy(PromptStrategy):
    """Extracts keywords from an abstract."""

    context = "You are a language model specializing in extracting concise and relevant keywords from text."

    def generate_prompt(self, title: str, abstract: str) -> dict:
        return {
            "instruction": "Extract exactly 4 keywords that represent the main topics of the abstract.",
            "title": title,
            "abstract": abstract
        }
