from typing import Dict

from enums import SDGType
from .strategy import PromptStrategy


class AnnotationEvaluatorStrategy(PromptStrategy):
    """Evaluates user annotations for relevance, depth, correctness, and creativity."""

    def __init__(self):
        self.context = (
            "You are a detailed evaluator of user annotations. Assess each annotation based on relevance, depth, correctness, and creativity."
        )

    def generate_prompt(self, passage: str, annotation: str, sdg_label: SDGType) -> Dict:
        return {
            "instruction": (
                "Evaluate the provided annotation based on the following dimensions:"
                "1. Relevance: How well does the annotation align with the SDG label and passage?"
                "2. Depth: Does the annotation provide insightful, detailed reasoning or evidence?"
                "3. Correctness: Is the information accurate and logically sound?"
                "4. Creativity: Does the annotation showcase originality or unique perspectives?"
                "Provide a score from 0-5 (integer) for each dimension and a short, concise reasoning."
            ),
            "passage": passage,
            "annotation": annotation,
             "sdg_label": sdg_label.value  # Convert SDGType enum to string
        }
