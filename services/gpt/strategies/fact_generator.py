from .strategy import PromptStrategy

class FactStrategy(PromptStrategy):
    """Generates a 'Did-You-Know' fact from an abstract."""

    def __init__(self):
        self.context = "You are a fact-generation assistant specializing in creating engaging 'Did-You-Know' facts from text."

    def generate_prompt(self, title: str, abstract: str) -> dict:
        return {
            "instruction": (
                "Create a single, catchy, and engaging sentence that summarizes this scientific abstract's key "
                "finding or idea. It should be accessible to a general audience and highlight the study's most "
                "interesting or surprising aspect."
            ),
            "title": title,
            "abstract": abstract
        }
