from typing import List, Dict

from .base_strategy import PromptStrategy


class SummarizeSinglePublicationStrategy(PromptStrategy):
    """ Summarizes a publication."""

    def __init__(self):
        self.context = "You are a summarization expert. Create a concise and informative summary of the given publication."

    def generate_prompt(self, title: str, abstract: str) -> dict:
        return {
            "instruction": (
                "Summarize the publication in one sentence with the highest possible information density, "
                "making it understandable and engaging for non-experts."
            ),
            "title": title,
            "abstract": abstract
        }

class SummarizeMultiplePublicationsStrategy(PromptStrategy):
    """Summarizes a set of publications into a single sentence and extracts keywords."""

    def __init__(self):
        self.context = "You are a summarization assistant. Generate a single cohesive summary and keywords for a group of publications."

    def generate_prompt(self, publications: List[Dict[str, str]]) -> dict:
        summaries = [
            f"Title: { pub.get('title', 'No Title')} Abstract: {pub.get('abstract', 'No Abstract')}"
            for pub in publications
        ]
        joined_summaries = "\n\n".join(summaries)
        return {
            "instruction": (
                "Generate a single cohesive sentence that captures the main themes across all the provided publications. "
                "Do not refer to individual publications or use phrases like 'the first study'. "
                "Even if the publications are unrelated, find overarching topics. "
                "Make the summary concise, engaging, and understandable for non-experts. "
                "Additionally, extract exactly 5 keywords that capture the overarching nature of the publications."
            ),
            "publications": joined_summaries
        }
