from typing import List, Dict

from sqlalchemy.orm import Session, joinedload

from models import SDGUserLabel, sdg_label_decision_user_label_association
from request_models.sdg_user_label import UserLabelRequest
from schemas import SDGLabelDistribution, SDGUserLabelStatisticsSchema, SDGUserLabelSchemaFull, UserVotingDetails
from services.decision_service import DecisionService
from settings.settings import TimeZoneSettings, LabelServiceSettings
from utils.logger import logger

time_zone_settings = TimeZoneSettings()
label_service_settings = LabelServiceSettings()

# Setup Logging
logging = logger(label_service_settings.LABEL_SERVICE_LOG_NAME)


class LabelService:
    def __init__(self, db: Session):
        self.db = db
        logging.info("LabelService initialized.")

    def create_or_link_label(self, request: UserLabelRequest) -> SDGUserLabel:
        """
        Create or link an SDGUserLabel.
        """
        logging.info("Creating or linking a label.")
        decision_service = DecisionService(self.db)
        decision = decision_service.find_or_create_decision(request)

        new_user_label = SDGUserLabel(
            user_id=request.user_id,
            publication_id=request.publication_id,
            voted_label=request.voted_label,
            abstract_section=request.abstract_section or "",
            comment=request.comment or "",
        )
        self.db.add(new_user_label)
        self.db.flush()
        logging.info("Created a new user label.")

        decision.user_labels.append(new_user_label)
        decision_service.calculate_consensus(decision)

        scenario = decision_service.evaluate_vote_scenario(decision.user_labels)
        logging.info(f"Evaluated scenario: {scenario}.")

        """      
        if scenario == ScenarioType.CONFIRM:
            logging.info("Handling manual confirmation for CONFIRM scenario.")
            decision_service.handle_manual_confirmation(decision, request.user_id, request.voted_label)
        """


        self.db.commit()
        self.db.refresh(new_user_label)
        logging.info("Label creation/linking completed.")
        return new_user_label


    def get_all_labels_for_decision(self, decision_id: int) -> List[SDGUserLabel]:
        """Retrieve all SDGUserLabels for a specific decision_id."""
        return (
            self.db.query(SDGUserLabel)
            .join(
                sdg_label_decision_user_label_association,
                sdg_label_decision_user_label_association.c.user_label_id == SDGUserLabel.label_id,
            )
            .filter(sdg_label_decision_user_label_association.c.decision_id == decision_id)
            .options(joinedload(SDGUserLabel.user))  # Eager load the user relationship
            .all()
        )

    def get_latest_labels_per_user(self, all_labels: List[SDGUserLabel]) -> List[SDGUserLabel]:
        """Filter and return only the latest label per user."""
        latest_labels_by_user = {}
        for label in all_labels:
            user_id = label.user_id
            if user_id not in latest_labels_by_user or label.labeled_at > latest_labels_by_user[user_id].labeled_at:
                latest_labels_by_user[user_id] = label
        return list(latest_labels_by_user.values())

    def calculate_label_distribution(self, labels: List[SDGUserLabel]) -> Dict[int, Dict]:
        """Calculate the distribution of labels, including user_ids."""
        distribution = {}
        for label in labels:
            voted_label = label.voted_label
            user_id = label.user_id
            if voted_label in distribution:
                distribution[voted_label]["count"] += 1
                distribution[voted_label]["user_ids"].append(user_id)
            else:
                distribution[voted_label] = {"count": 1, "user_ids": [user_id]}
        return distribution

    def calculate_user_voting_details(self, labels: List[SDGUserLabel]) -> Dict[int, List[int]]:
        """Calculate voting details for each user."""
        user_voting_details = {}
        for label in labels:
            user_id = label.user_id
            voted_label = label.voted_label
            if user_id in user_voting_details:
                user_voting_details[user_id].append(voted_label)
            else:
                user_voting_details[user_id] = [voted_label]
        return user_voting_details

    def get_statistics(self, decision_id: int) -> SDGUserLabelStatisticsSchema:
        """Retrieve statistics for SDGUserLabels, including label distribution, user voting details, and full entities."""
        # Get all labels for the decision
        all_labels = self.get_all_labels_for_decision(decision_id)

        # Get the latest labels per user
        latest_labels = self.get_latest_labels_per_user(all_labels)

        # Calculate raw label distribution (all votes)
        raw_label_distribution = self.calculate_label_distribution(all_labels)

        # Calculate filtered label distribution (only latest votes)
        filtered_label_distribution = self.calculate_label_distribution(latest_labels)

        # Calculate user voting details (all votes, not just the latest)
        user_voting_details = self.calculate_user_voting_details(all_labels)

        # Convert distributions to the schema format
        total_label_distribution_schema = [
            SDGLabelDistribution(sdg_label=label, count=data["count"], user_ids=data["user_ids"])
            for label, data in raw_label_distribution.items()
        ]
        label_distribution_schema = [
            SDGLabelDistribution(sdg_label=label, count=data["count"], user_ids=data["user_ids"])
            for label, data in filtered_label_distribution.items()
        ]

        # Convert user voting details to the schema format
        user_voting_details_schema = [
            UserVotingDetails(user_id=user_id, voted_labels=labels)
            for user_id, labels in user_voting_details.items()
        ]

        # Convert the latest labels to the schema format
        sdg_user_labels_schema = [
            SDGUserLabelSchemaFull.model_validate(label) for label in latest_labels
        ]

        # Return the statistics and full entities
        return SDGUserLabelStatisticsSchema(
            label_distribution=label_distribution_schema,
            total_label_distribution=total_label_distribution_schema,
            user_voting_details=user_voting_details_schema,
            sdg_user_labels=sdg_user_labels_schema,
        )
