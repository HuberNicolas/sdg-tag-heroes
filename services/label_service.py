from typing import List, Dict

from sqlalchemy.orm import Session, joinedload

from enums import SDGType
from enums.enums import ScenarioType, LevelType
from models import SDGUserLabel, sdg_label_decision_user_label_association, SDGPrediction, SDGXPBankHistory, \
    SDGCoinWalletHistory
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

    ## **Reward Logic**
    ---
    1. **User submits a label (i.e., votes for an SDG):**
       - **XP is only awarded after the decision is finalized** (not immediate).
       - **Coins are awarded in fixed amounts (100, 200, or 300)** based on task difficulty.

    2. **User submits a label with a comment:**
       - Earns XP and coins as described above.
       - Additionally, **immediate XP** is granted for knowledge externalization (comment quality).
       - If the label was correct, an **extra 100% XP is awarded after finalization**.

    3. **User submits a label with a comment & abstract selection:**
       - Follows the same reward pattern as above.
       - Earns **higher XP rewards** due to detailed knowledge externalization.

    ## **XP vs. Coin Rewards**
    ---
    **Coins:**
    - **Fixed** rewards (static amounts) based on task difficulty:
      - **Bronze Task** → 100 Coins
      - **Silver Task** → 200 Coins
      - **Gold Task** → 300 Coins
    - **Only awarded after decision finalization** to users who voted for the final SDG label.

    **XP:**
    - **Dynamically calculated** based on multiple factors:
      - **Immediate XP** → Based on **comment quality** (evaluated using Annotation Evaluation).
      - **Final XP (post-decision)** → Based on SDG correctness and decision entropy.
    - **Exploration Case (Multiple SDGs):**
      - XP is determined by entropy, rewarding users based on decision complexity.
      - Formula: `XP = 10 * entropy` (ranging from **7 - 85 XP**).
    - **Single SDG Case:**
      - XP is calculated using a scoring function based on **vote confidence**.

    ## **Notes**
    ---
    - **XP from comments is granted immediately**, while XP from labeling is **only given after decision finalization**.
    - **Coins are static**, while **XP is dynamic and changes based on user input and decision confidence**.
    - Users submitting **low-quality or spam comments may receive reduced XP rewards**.
    - The system ensures that contributions are meaningful and aligned with the correct SDG labels.
    """

    def __init__(self, db: Session):
        self.db = db
        self.reward_service = RewardService(db)
        logging.info("LabelService initialized.")

    def create_or_link_label(self, request: UserLabelRequest, is_single_sdg: bool = True) -> SDGUserLabel:
        """
        Create or link an SDGUserLabel, evaluate rewards, and apply a dynamic scoring function.

        Args:
            request (UserLabelRequest): The request containing user label data.
            is_single_sdg (bool, optional): A flag to determine if the decision involves a single SDG.
                                            If not provided, it will be computed dynamically.
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
            P_max = 1.0  # Fallback if no prediction exists
            entropy_xp = 10  # Placeholder entropy
        else:
            # Get probability of the SDG the user voted for
            voted_sdg_key = f"sdg{request.voted_label}"
            P_max = getattr(prediction, voted_sdg_key, 0.0)  # Probability of the voted SDG
            entropy_xp = prediction.entropy  # Entropy from prediction model



        """
            score_value = 0
            if is_single_sdg:
            # **Single SDG Case → Scoring Function Based on Votes**
            user_votes = len(decision.user_labels)
            score_value = score(user_votes, P_max)
            logging.info(f"Computed score for Single SDG case (Label {new_user_label.label_id}): {score_value:.2f}")

        else:
            # **Multiple SDG Case → Use Entropy-Based XP**
            score_value = 10 * entropy_xp  # Scaling entropy to XP system
            logging.info(f"Computed score for Multiple SDG case (Label {new_user_label.label_id}): {score_value:.2f}")
        """


        # **Immediate XP Reward Calculation**
        xp_reward = self.reward_service._calculate_xp(new_user_label)
        logging.info(f"XP Rewarded: {xp_reward} for user label {new_user_label.label_id}")

        # **Convert voted_label (int) to SDGType Enum**
        new_user_sdg_enum_value = SDGType[f"SDG_{new_user_label.voted_label}"]

        # **Log XP Gain in SDGXPBankHistory**
        xp_history_entry = SDGXPBankHistory(
            xp_bank_id=request.user_id,  # Assuming XP bank is linked to user ID
            sdg=new_user_sdg_enum_value,
            increment=xp_reward,
            reason="Initial XP reward for SDG labeling",
            is_shown=True,
        )
        self.db.add(xp_history_entry)
        logging.info(f"Logged XP transaction for user {request.user_id}: {xp_reward} XP.")

        # **Final Coin & XP Reward if Consensus is Reached**
        if decision.decided_label:

            # **Determine Task Difficulty Based on SDG Probability**
            voted_sdg_key = f"sdg{request.voted_label}"
            P_max = getattr(prediction, voted_sdg_key, 0.0)  # Probability of the voted SDG

            level = LevelType.get_level(P_max)
            coin_reward = level.coins

            logging.info(
                f"Consensus reached! Awarding {coin_reward} Coins (Level: {level}, ({level.min_prob}) -  ({level.max_prob}), (Prediction: {P_max} for {voted_sdg_key})) to users who voted correctly.")

            # **Sort labels by created_at to calculate score incrementally**
            sorted_labels = sorted(decision.user_labels, key=lambda x: x.labeled_at)

            # **Award XP & Coins to All Users Who Voted Correctly**
            for idx, label in enumerate(sorted_labels):
                if label.voted_label == decision.decided_label:
                    # **Calculate score based on the number of votes up to this point**
                    user_votes = idx + 1  # Incremental votes
                    score_value = score(user_votes, P_max) if is_single_sdg else 10 * entropy_xp

                    # **Base XP is now the score_value**
                    base_xp = score_value

                    additional_xp = self.reward_service._calculate_xp(label)
                    total_xp = additional_xp + base_xp
                    logging.info(f"User {label.user_id} gets {total_xp} XP and {coin_reward} Coins.")

                    # **Convert voted_label (int) to SDGType Enum**
                    sdg_enum_value = SDGType[f"SDG_{label.voted_label}"]

                    # **Log Base XP in SDGXPBankHistory**
                    base_xp_entry = SDGXPBankHistory(
                        xp_bank_id=label.user_id,
                        sdg=sdg_enum_value,
                        increment=base_xp,
                        reason=f"Base XP for SDG {label.voted_label} after decision consensus (Publication {decision.publication_id})",
                        is_shown=False,
                    )
                    self.db.add(base_xp_entry)
                    logging.info(f"Logged Base XP transaction for user {label.user_id}: +{base_xp} XP.")

                    # **Log Comment Bonus XP in SDGXPBankHistory (If Applicable)**
                    if label.comment:
                        comment_xp_entry = SDGXPBankHistory(
                            xp_bank_id=label.user_id,
                            sdg=sdg_enum_value,
                            increment=additional_xp,
                            reason=f"Bonus XP for providing a comment on SDG {label.voted_label} (Publication {decision.publication_id})",
                            is_shown=False,
                        )
                        self.db.add(comment_xp_entry)
                        logging.info(
                            f"Logged Comment Bonus XP transaction for user {label.user_id}: +{additional_xp} XP.")

                    # **Log Coin Reward in SDGCoinWalletHistory**
                    coin_entry = SDGCoinWalletHistory(
                        wallet_id=label.user_id,
                        increment=coin_reward,
                        reason=f"Final coin reward for SDG {label.voted_label} after decision consensus (Publication {decision.publication_id})",
                        is_shown=False,
                    )
                    self.db.add(coin_entry)
                    logging.info(f"Logged coin transaction for user {label.user_id}: +{coin_reward} Coins.")

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
