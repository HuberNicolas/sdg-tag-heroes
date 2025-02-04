import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from enums.enums import DecisionType, ScenarioType
from models import SDGLabelDecision, SDGLabelHistory, SDGLabelSummary, SDGPrediction, SDGUserLabel
from models.publications.publication import Publication
from request_models.sdg_user_label import UserLabelRequest
from settings.settings import TimeZoneSettings, DecisionServiceSettings
from utils.logger import logger

time_zone_settings = TimeZoneSettings()
decision_service_settings = DecisionServiceSettings()

# Setup Logging
logging = logger(decision_service_settings.DECISION_SERVICE_LOG_NAME)


class DecisionService:
    def __init__(self, db: Session):
        self.db = db
        logging.info("DecisionService initialized.")

    def get_most_recent_labels_per_user(self, user_labels: List["SDGUserLabel"]) -> List[int]:
        """
        Get the most recent voted_label for each user.
        """
        user_to_label = {}  # Maps user_id to their most recent voted_label
        for label in user_labels:
            if label.user_id not in user_to_label or label.labeled_at.replace(tzinfo=None) > user_to_label[
                label.user_id].labeled_at.replace(tzinfo=None):
                user_to_label[label.user_id] = label
        return [label.voted_label for label in user_to_label.values()]

    def evaluate_vote_scenario(self, user_labels: List["SDGUserLabel"], votes_needed: int = decision_service_settings.VOTES_NEEDED_FOR_SCENARIO) -> ScenarioType:
        """
        Evaluate the current scenario based on the distribution of votes.
        Only the most recent label per user is counted.
        """
        logging.info("Evaluating vote scenario.")
        most_recent_labels = self.get_most_recent_labels_per_user(user_labels)

        if len(most_recent_labels) < votes_needed:
            logging.info("Not enough votes to trigger a scenario.")
            return ScenarioType.NOT_ENOUGH_VOTES

        # Count the occurrences of each label
        vote_counts = Counter(most_recent_labels)
        sorted_counts = sorted(vote_counts.values(), reverse=True)

        # Total number of votes
        total_votes = len(most_recent_labels)

        # Thresholds (relative to total_votes)
        absolute_majority_threshold = total_votes * 0.5  # More than 50% for Confirm
        significant_count_threshold = total_votes * 0.3  # At least 30% for Investigate

        # Scenario 1: Confirm (Absolute majority > 50% for one class)
        if sorted_counts[0] > absolute_majority_threshold:
            logging.info("Scenario: Confirm (Absolute majority).")
            return ScenarioType.CONFIRM

        # Scenario 2: Tiebreaker (50/50 split between exactly two classes)
        if len(sorted_counts) == 2 and sorted_counts[0] == sorted_counts[1] and sorted_counts[0] == total_votes / 2:
            logging.info("Scenario: Tiebreaker (50/50 split).")
            return ScenarioType.TIEBREAKER

        # Scenario 3: Investigate (More than 2 classes with significant counts)
        if len(sorted_counts) >= 3 and sorted_counts[0] >= significant_count_threshold and sorted_counts[1] >= significant_count_threshold:
            logging.info("Scenario: Investigate (Multiple significant counts).")
            return ScenarioType.INVESTIGATE

        # Scenario 4: Explore (No clear majority, multiple classes with low counts)
        if sorted_counts[0] <= significant_count_threshold and len(sorted_counts) >= 3:
            logging.info("Scenario: Explore (No clear majority).")
            return ScenarioType.EXPLORE

        logging.info("Scenario: No specific scenario.")
        return ScenarioType.NO_SPECIFIC_SCENARIO

    def calculate_consensus(self, decision: SDGLabelDecision) -> None:
        """
        Calculate consensus for the given decision and update it.
        Only the most recent label per user is counted.
        """
        logging.info("Calculating consensus.")
        most_recent_labels = self.get_most_recent_labels_per_user(decision.user_labels)
        total_votes = len(most_recent_labels)

        if total_votes >= decision_service_settings.VOTES_NEEDED_FOR_CONSENSUS:
            vote_counts = Counter(most_recent_labels)
            max_votes = max(vote_counts.values())
            if max_votes > total_votes / 2:  # Clear majority
                winning_label = vote_counts.most_common(1)[0][0]
                logging.info(f"Consensus reached for label {winning_label}.")
                self.finalize_decision(decision, winning_label)
            else:
                logging.info("No consensus reached. Leaving decision open.")
                decision.decided_label = 0  # Leave decision open
        else:
            logging.info("Not enough votes for consensus. Leaving decision open.")
            decision.decided_label = 0  # Not enough votes for consensus

        self.db.commit()

    def finalize_decision(self, decision: SDGLabelDecision, winning_label: int) -> None:
        """
        Finalize the decision and update the label summary.
        """
        logging.info(f"Finalizing decision with winning label {winning_label}.")
        decision.decided_label = winning_label
        decision.decided_at = datetime.now(time_zone_settings.ZURICH_TZ)
        decision.decision_type = DecisionType.CONSENSUS_MAJORITY
        self.db.commit()

        self.update_label_summary(decision)

    def update_label_summary(self, decision: SDGLabelDecision) -> None:
        """
        Update the SDGLabelSummary based on the finalized decision.
        """
        logging.info("Updating label summary.")
        label_summary = decision.history.label_summary
        if not label_summary:
            logging.error("SDGLabelSummary not found for the decision.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SDGLabelSummary not found for the decision.",
            )

        if decision.decided_label == 18:  # Null class
            logging.info("Setting all SDGs to -1 (Null class).")
            for i in range(1, 18):
                setattr(label_summary, f"sdg{i}", -1)
        else:  # SDG label (1-17)
            logging.info(f"Setting SDG {decision.decided_label} to 1.")
            setattr(label_summary, f"sdg{decision.decided_label}", 1)

        self.db.commit()

    def handle_manual_confirmation(self, decision: SDGLabelDecision, user_id: int, confirmed_label: int) -> None:
        """
        Handle manual confirmation of a label in the CONFIRM scenario.
        """
        logging.info("Handling manual confirmation.")
        if decision.decision_type != DecisionType.CONSENSUS_MAJORITY:
            logging.error("Manual confirmation is only allowed in the CONFIRM scenario.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manual confirmation is only allowed in the CONFIRM scenario.",
            )

        most_recent_labels = self.get_most_recent_labels_per_user(decision.user_labels)
        majority_label = self.has_clear_majority(most_recent_labels, len(most_recent_labels))
        if majority_label != confirmed_label:
            logging.error("Confirmed label does not match the majority.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmed label does not match the majority.",
            )

        self.finalize_decision(decision, confirmed_label)

    def has_clear_majority(self, votes: List[int], total_votes: int) -> Optional[int]:
        """
        Check if there is a clear majority for a label.
        """
        logging.info("Checking for clear majority.")
        vote_counts = Counter(votes)
        max_votes = max(vote_counts.values())
        if max_votes > total_votes / 2:
            winning_label = vote_counts.most_common(1)[0][0]
            logging.info(f"Clear majority found for label {winning_label}.")
            return winning_label
        logging.info("No clear majority found.")
        return None

    def find_or_create_decision(self, request: UserLabelRequest) -> SDGLabelDecision:
        """
        Find or create an SDGLabelDecision based on the provided data.
        """
        logging.info("Finding or creating a decision.")
        if request.decision_id:
            logging.info(f"Decision ID provided: {request.decision_id}.")
            decision = self.db.query(SDGLabelDecision).filter(
                SDGLabelDecision.decision_id == request.decision_id
            ).first()
            if not decision:
                logging.error(f"Decision with ID {request.decision_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"SDGLabelDecision with ID {request.decision_id} not found",
                )
            return decision

        if not request.publication_id:
            logging.error("Neither decision_id nor publication_id provided.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either publication_id or decision_id must be provided",
            )

        publication = self.db.query(Publication).filter(
            Publication.publication_id == request.publication_id
        ).first()
        if not publication:
            logging.error(f"Publication with ID {request.publication_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {request.publication_id} not found",
            )

        sdg_label_summary = self.db.query(SDGLabelSummary).filter(
            SDGLabelSummary.publication_id == publication.publication_id
        ).first()
        if not sdg_label_summary:
            logging.error("SDGLabelSummary not found for the given publication.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SDGLabelSummary not found for the given publication",
            )

        history = self.db.query(SDGLabelHistory).filter(
            SDGLabelHistory.history_id == sdg_label_summary.history_id
        ).first()
        if not history:
            logging.error("SDGLabelHistory not found for the given summary.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SDGLabelHistory not found for the given summary",
            )

        sdg_prediction = self.db.query(SDGPrediction).filter(
            SDGPrediction.publication_id == publication.publication_id,
            SDGPrediction.prediction_model == decision_service_settings.DEFAULT_MODEL
        ).first()

        highest_sdg_number = None
        if sdg_prediction:
            highest_sdg_key, highest_sdg_number, highest_sdg_value = sdg_prediction.get_highest_sdg()
            logging.info(
                f"Highest SDG prediction: {highest_sdg_key} ({highest_sdg_number}), Value: {highest_sdg_value}.")

        unfinished_decision = next((d for d in history.decisions if d.decided_label == 0), None)
        if unfinished_decision:
            logging.info("Found an unfinished decision.")
            return unfinished_decision

        decision = SDGLabelDecision(
            suggested_label=highest_sdg_number,
            history_id=history.history_id,
            decision_type=request.decision_type,
            decided_at=datetime.now(),
        )
        self.db.add(decision)
        self.db.flush()
        logging.info("Created a new decision.")
        return decision
