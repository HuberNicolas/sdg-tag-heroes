
# Strategy Implementation
class PromptStrategy:
    """Base class for prompt strategies."""
    context: str

    def generate_prompt(self, *args, **kwargs) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")
