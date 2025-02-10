from sqlalchemy.orm import Session
from services.gpt.gpt_assistant_service import GPTAssistantService
from services.gpt.user_annotation_evaluator_service import UserAnnotationEvaluatorService
from models import SDGLabelDecision, SDGPrediction, SDGUserLabel
from enums.enums import SDGType
from settings.settings import RewardServiceSettings
from utils.logger import logger

# Setup Logging
reward_service_settings = RewardServiceSettings()
logging = logger(reward_service_settings.REWARD_SERVICE_LOG_NAME)

# Difficulty coin mapping
DIFFICULTY_REWARD = {"Bronze": 100, "Silver": 200, "Gold": 300}


class RewardService:
    def __init__(self, db: Session):
        self.db = db
        self.gpt_service = GPTAssistantService()
        self.evaluator_service = UserAnnotationEvaluatorService()
        logging.info("RewardService initialized.")

    def xp_evaluate_user_label_comment(self, label: SDGUserLabel) -> float:
        """
        Evaluate the user's comment and abstract section for knowledge externalization.
        Returns an evaluation score, or 0.0 if insufficient data is provided.
        """
        if not label.comment or not label.abstract_section:
            logging.info(f"Skipping evaluation for label {label.label_id}: No comment or abstract section provided.")
            return 0.0  # No XP for missing comments

        voted_user_sdg_key = f"sdg{label.voted_label}" if label.voted_label else "sdg0"

        # Get LLM-based evaluation scores
        llm_scores = self.gpt_service.evaluate_annotation(
            passage=label.abstract_section,
            annotation=label.comment,
            sdg_label=SDGType(voted_user_sdg_key),
        )

        # Get semantic similarity and final combined score
        evaluation_result = self.evaluator_service.evaluate_annotation(
            passage=label.abstract_section,
            annotation=label.comment,
            sdg_label=SDGType(voted_user_sdg_key),
            llm_scores=llm_scores,
        )

        logging.info(f"Comment evaluation for label {label.label_id}: {evaluation_result.combined_score:.2f}")

        return evaluation_result.combined_score  # Score for XP calculation

    def _calculate_xp(self, label: SDGUserLabel) -> int:
        """
        Calculate XP dynamically based on knowledge externalization and decision agreement.
        """
        xp = 0

        # XP from knowledge externalization
        comment_xp = self.xp_evaluate_user_label_comment(label) * 10  # Scale to XP system
        xp += round(comment_xp)

        logging.info(f"Total XP for label {label.label_id}: {xp}")
        return xp
