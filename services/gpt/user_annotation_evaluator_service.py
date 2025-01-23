from transformers import AutoTokenizer, AutoModel

from enums import SDGType
from schemas.gpt_assistant.gpt_assistant import GPTResponseAnnotationScoreSchema, AnnotationEvaluationSchema
from settings.sdg_descriptions import sdgs
import torch

import os

from settings.settings import UserAnnotationAssessmentSettings

# OpenBLAS Warning : Detect OpenMP Loop and this application may hang. Please rebuild the library with USE_OPENMP=1 option.
os.environ["OPENBLAS_NUM_THREADS"] = "1"


user_annotation_assessment_settings = UserAnnotationAssessmentSettings()


# Load Transformer Model
tokenizer = AutoTokenizer.from_pretrained(user_annotation_assessment_settings.BERT_PRETRAINED_MODEL_NAME)
model = AutoModel.from_pretrained(user_annotation_assessment_settings.BERT_PRETRAINED_MODEL_NAME)

class UserAnnotationEvaluatorService:
    """Service for evaluating annotations with semantic similarity and combined scoring."""

    def calculate_semantic_similarity(self, annotation: str, sdg_label_description: str) -> float:
        """Calculates semantic similarity between annotation and SDG description."""

        # Encode annotation and SDG description
        annotation_embedding = model(**tokenizer(annotation, return_tensors="pt", truncation=True, padding=True))
        sdg_embedding = model(**tokenizer(sdg_label_description, return_tensors="pt", truncation=True, padding=True))

        # Extract CLS token embeddings and ensure tensors are 1-dimensional
        annotation_vector = annotation_embedding.last_hidden_state[:, 0, :].squeeze(0)
        sdg_vector = sdg_embedding.last_hidden_state[:, 0, :].squeeze(0)

        # Compute cosine similarity
        similarity = torch.nn.functional.cosine_similarity(annotation_vector, sdg_vector, dim=0).item()
        return similarity

    def evaluate_annotation(self, passage: str, annotation: str, sdg_label: SDGType, llm_scores: GPTResponseAnnotationScoreSchema) -> AnnotationEvaluationSchema:
        """Combines LLM and semantic similarity scores."""

        # Convert SDGType enum to string (e.g., SDGType.SDG_1 -> "sdg1")
        sdg_label_str = sdg_label.value

        # Extract the numeric part of the SDG label (e.g., "sdg1" -> 1)
        sdg_index = int(sdg_label_str.replace("sdg", ""))

        # TODO: add 0 and 18 class
        sdg_description = next((sdg.sdg_description for sdg in sdgs if sdg.index == sdg_index), None)
        if not sdg_description:
            raise ValueError(f"Invalid SDG index: {sdg_label}")

        semantic_score = self.calculate_semantic_similarity(annotation, sdg_description)

        llm_avg_score = (
            llm_scores.relevance + llm_scores.depth + llm_scores.correctness + llm_scores.creativity
        ) / 4

        combined_score = (0.5 * llm_avg_score + 0.5 * semantic_score)

        return AnnotationEvaluationSchema(
            passage=passage,
            annotation=annotation,
            sdg_label=sdg_label,  # Use the SDGType enum
            relevance=llm_scores.relevance,
            depth=llm_scores.depth,
            correctness=llm_scores.correctness,
            creativity=llm_scores.creativity,
            reasoning=llm_scores.reasoning,
            llm_score=llm_avg_score,
            semantic_score=semantic_score,
            combined_score=combined_score,
        )
