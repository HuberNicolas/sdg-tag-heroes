from sqlalchemy.orm import Session

from models import SDGLabelDecision, SDGCoinWallet, \
    SDGCoinWalletHistory
from settings.settings import TimeZoneSettings, RewardServiceSettings
from utils.logger import logger

time_zone_settings = TimeZoneSettings()
reward_service_settings = RewardServiceSettings()


# Setup Logging
logging = logger(reward_service_settings.REWARD_SERVICE_LOG_NAME)

class RewardService:
    def __init__(self, db: Session):
        self.db = db
        logging.info("RewardService initialized.")

    def reward_users(self, decision: SDGLabelDecision) -> None:
        """
        Reward users based on their votes in the decision.
        The winning label gets 100 coins, the second most common label gets 50 coins.
        """
        logging.info("Rewarding users.")
        winning_label = decision.decided_label
        if winning_label == -1:
            logging.info("No reward: No decision made.")
            return

        # Count votes for each label
        vote_counts = {}
        user_votes = {}

        for label in decision.user_labels:
            user_votes.setdefault(label.user_id, set()).add(label.voted_label)
            vote_counts[label.voted_label] = vote_counts.get(label.voted_label, 0) + 1

        # Identify the second most common label
        sorted_labels = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
        second_label = sorted_labels[1][0] if len(sorted_labels) > 1 else None

        for user_id, voted_labels in user_votes.items():
            wallet = self.db.query(SDGCoinWallet).filter(SDGCoinWallet.user_id == user_id).first()
            if not wallet:
                logging.warning(f"Wallet not found for user {user_id}.")
                continue

            # Determine the reward
            if winning_label in voted_labels:
                increment = 100  # Full reward
                reason = f"Reward for voting for the winning SDG {winning_label}."
            elif second_label and second_label in voted_labels:
                increment = 50  # Half reward
                reason = f"Partial reward for voting for SDG {second_label} (2nd most common)."
            else:
                increment = 0  # No reward
                reason = f"No reward: Did not vote for SDG {winning_label} or {second_label}."

            """
            # Future Work
            
            # Apply penalty if user voted for more than 3 labels
            if len(voted_labels) > 3:
                penalty = -10 * (len(voted_labels) - 3)
                increment += penalty
                reason += f" Penalty for voting on too many SDGs ({len(voted_labels)})."
            
            """

            if increment != 0:
                wallet.total_coins += increment
                wallet_history = SDGCoinWalletHistory(
                    wallet_id=wallet.sdg_coin_wallet_id,
                    increment=increment,
                    reason=reason,
                )
                self.db.add(wallet_history)
                logging.info(f"User {user_id} updated: {increment} coins. {reason}")

        self.db.commit()
        logging.info("User rewards processed.")

