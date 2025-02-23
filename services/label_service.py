from typing import List, Dict

from sqlalchemy.orm import Session, joinedload

from enums import SDGType
from enums.enums import ScenarioType, LevelType
from models import SDGUserLabel, sdg_label_decision_user_label_association, SDGPrediction, SDGXPBankHistory, \
    SDGCoinWalletHistory, SDGCoinWallet, SDGXPBank
from request_models.sdg_user_label import UserLabelRequest
from schemas import SDGLabelDistribution, SDGUserLabelStatisticsSchema, SDGUserLabelSchemaFull, UserVotingDetails
from services.decision_service import DecisionService
from services.reward_service import RewardService
from services.scoring_service import score
from settings.settings import TimeZoneSettings, LabelServiceSettings
from utils.logger import logger

time_zone_settings = TimeZoneSettings()
label_service_settings = LabelServiceSettings()

# Setup Logging
logging = logger(label_service_settings.LABEL_SERVICE_LOG_NAME)


class LabelService:
    """
    Handles the reward distribution system for users participating in SDG labeling.

    This service ensures fair allocation of **XP (experience points)** and **coins** to incentivize
    user participation and improve labeling quality.
    """

    def __init__(self, db: Session):
        self.db = db
        self.reward_service = RewardService(db)
        logging.info("LabelService initialized.")

    def create_or_link_label(self, request: UserLabelRequest) -> SDGUserLabel:
        """
        Create or link an SDGUserLabel, evaluate rewards, and apply a dynamic scoring function.

        Args:
            request (UserLabelRequest): The request containing user label data.
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
        old_scenario = decision.scenario_type

        logging.info("Check new scenario and update scenario in decision based on new user label.")
        scenario = decision_service.evaluate_vote_scenario(decision.user_labels)

        logging.info(f"Update scenario in decision based on new user label: Old scenario {old_scenario}; New scenario {scenario}.")
        decision.scenario_type = scenario

        logging.info("Check consensus - can we finalize this label?")
        decision_service.calculate_consensus(decision)

        # Rewards
        # **Fetch SDG Prediction for the Publication**
        prediction = (
            self.db.query(SDGPrediction)
            .filter(SDGPrediction.publication_id == request.publication_id)
            .filter(SDGPrediction.prediction_model == "Aurora")
            .first()
        )

        if not prediction:
            logging.warning(f"No SDG prediction found for publication {request.publication_id}. Using default values.")
        else:
            # Get probability of the SDG the user voted for
            voted_sdg_key = f"sdg{request.voted_label}"

        # **Immediate XP Reward Calculation**

        base_xp = prediction.entropy * 10
        additional_xp = self.reward_service._calculate_xp(new_user_label)
        total_xp = int(additional_xp + base_xp)

        logging.info(
            f"User {new_user_label.user_id} gets {total_xp} = {base_xp} (Base) + {additional_xp} (Additional) XP.")

        # **Convert voted_label (int) to SDGType Enum**
        new_user_sdg_enum_value = SDGType[f"SDG_{new_user_label.voted_label}"]

        # **Fetch the user's XP bank**
        xp_bank = self.db.query(SDGXPBank).filter(SDGXPBank.user_id == request.user_id).first()

        if not xp_bank:
            raise ValueError(f"No XP bank found for user {request.user_id}")

        # **Update total XP and specific SDG XP**
        xp_bank.total_xp += total_xp

        # **Determine which SDG field to update**
        sdg_xp_field = f"sdg{request.voted_label}_xp"

        if hasattr(xp_bank, sdg_xp_field):
            setattr(xp_bank, sdg_xp_field, getattr(xp_bank, sdg_xp_field) + total_xp)
        else:
            raise ValueError(f"Invalid SDG XP field: {sdg_xp_field}")

        # **Log XP Gain in SDGXPBankHistory**
        xp_history_entry = SDGXPBankHistory(
            xp_bank_id=request.user_id,
            sdg=new_user_sdg_enum_value,
            increment=total_xp,
            reason=f"Initial XP reward for SDG labeling of the Publication {request.publication_id}",
            is_shown=False,
        )
        self.db.add(xp_history_entry)
        logging.info(f"Logged XP transaction for user {request.user_id}: {total_xp} XP.")

        # **Final Coin & XP Reward if Consensus is Reached**
        if decision.decided_label:

            # **Determine Task Difficulty Based on SDG Probability**
            voted_sdg_key = f"sdg{request.voted_label}"
            P_max = getattr(prediction, voted_sdg_key, 0.0)  # Probability of the voted SDG
            level = LevelType.get_level(P_max)

            logging.info(
                f"Consensus reached! (Level: {level}, ({level.min_prob}) -  ({level.max_prob}), (Prediction: {P_max} for {voted_sdg_key})) to users who voted correctly.")

            # **Sort labels by created_at to calculate score incrementally**
            sorted_labels = sorted(decision.user_labels, key=lambda x: x.labeled_at)

            rewarded_user_ids = []

            # **Award XP & Coins to All Users Who Voted Correctly**
            for idx, label in enumerate(sorted_labels):
                if label.voted_label == decision.decided_label:

                    if label.user_id in rewarded_user_ids:
                        logging.info(f"User {label.user_id} has already received a coin reward. Skipping reward.")
                        continue  # Skip if user has already been rewarded

                    # **Calculate score based on the number of votes up to this point**
                    user_votes = idx + 1  # Incremental votes

                    coin_reward = score(user_votes, P_max)

                    # **Retrieve or Create SDGCoinWallet**
                    user_wallet = self.db.query(SDGCoinWallet).filter(SDGCoinWallet.user_id == label.user_id).first()
                    if not user_wallet:
                        user_wallet = SDGCoinWallet(user_id=label.user_id, total_coins=0.0)
                        self.db.add(user_wallet)

                    # **Update the total coins**
                    user_wallet.total_coins += coin_reward

                    # **Log Coin Reward in SDGCoinWalletHistory**
                    coin_entry = SDGCoinWalletHistory(
                        wallet_id=label.user_id,
                        increment=coin_reward,
                        reason=f"Final coin reward for SDG {label.voted_label} after decision consensus Publication {decision.publication_id}",
                        is_shown=False,
                    )
                    self.db.add(coin_entry)
                    logging.info(
                        f"Logged coin transaction for user {label.user_id}: +{coin_reward} Coins. Updated total: {user_wallet.total_coins}")

                    rewarded_user_ids.append(label.user_id)

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
