from typing import List, Dict

from .base_strategy import PromptStrategy

class SummarizeSDGUserLabelCommentsStrategy(PromptStrategy):
    """Summarizes a set of SDG user label comments into a single cohesive comment."""

    def __init__(self):
        self.context = "You are a summarization assistant. Generate a single cohesive summary for a collection of SDG user comments."

    def generate_prompt(self, user_labels: List[Dict[str, str]]) -> dict:
        comments = [
            f"Comment: {label.get('comment', 'No Comment')}"
            for label in user_labels
        ]
        joined_comments = "\n\n".join(comments)
        return {
            "instruction": (
                "Generate a single cohesive sentence that captures the main themes across all the provided comments. "
                "Do not refer to individual comments. Find overarching topics and themes from the collection of comments. "
                "Make the summary concise, engaging, and understandable for non-experts. "
            ),
            "user_labels": joined_comments
        }
