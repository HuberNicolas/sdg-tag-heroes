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
        """
        logging.info("Rewarding users.")
        winning_label = decision.decided_label
        if winning_label == -1:
            logging.info("No reward: No decision made.")
            return

        user_votes = {}
        for label in decision.user_labels:
            if label.user_id not in user_votes:
                user_votes[label.user_id] = set()
            user_votes[label.user_id].add(label.voted_label)

        winners = [user_id for user_id, user_set in user_votes.items() if winning_label in user_set]

        for user_id in user_votes:
            wallet = self.db.query(SDGCoinWallet).filter(SDGCoinWallet.user_id == user_id).first()
            if not wallet:
                logging.warning(f"Wallet not found for user {user_id}.")
                continue

            if user_id in winners:
                increment = 100 if len(user_votes[user_id]) <= 3 else -10 * (len(user_votes[user_id]) - 3)
                reason = f"Reward for voting for SDG {winning_label}." if increment > 0 else f"Penalty for voting on too many SDGs (limit 3)."
                logging.info(f"User {user_id} rewarded: {increment} coins.")
            else:
                increment = 0
                reason = f"No reward: Did not vote for SDG {winning_label}."
                logging.info(f"User {user_id} not rewarded.")

            if increment != 0:
                wallet.total_coins += increment
                wallet_history = SDGCoinWalletHistory(
                    wallet_id=wallet.sdg_coin_wallet_id,
                    increment=increment,
                    reason=reason,
                )
                self.db.add(wallet_history)
                logging.info(f"Wallet history updated for user {user_id}.")

        self.db.commit()
        logging.info("User rewards processed.")
