from enum import Enum as PyEnum
from typing import Tuple


class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"
    LABELER = "labeler"
    EXPERT = "expert"

class DecisionType(PyEnum):
    CONSENSUS_MAJORITY = "Consensus Majority"
    CONSENSUS_TECHNOCRATIC = "Consensus Technocratic"
    EXPERT_DECISION = "Expert Decision"

class VoteType(PyEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class SDGType(PyEnum):
    SDG_1 = "sdg1"
    SDG_2 = "sdg2"
    SDG_3 = "sdg3"
    SDG_4 = "sdg4"
    SDG_5 = "sdg5"
    SDG_6 = "sdg6"
    SDG_7 = "sdg7"
    SDG_8 = "sdg8"
    SDG_9 = "sdg9"
    SDG_10 = "sdg10"
    SDG_11 = "sdg11"
    SDG_12 = "sdg12"
    SDG_13 = "sdg13"
    SDG_14 = "sdg14"
    SDG_15 = "sdg15"
    SDG_16 = "sdg16"
    SDG_17 = "sdg17"

    # In sdg_label decision:
    SDG_0 = "sdg0"  # not defined
    SDG_18 = "sdg18" # zero class

class ScenarioType(PyEnum):
    CONFIRM = "Confirm" # Crown the Champion: 6, 4
    TIEBREAKER = "Tiebreaker" # Tip the Scales: 5, 5
    INVESTIGATE = "Investigate" # Unravel the Mystery: 3, 3, 3, 1
    EXPLORE = "Explore" # Chart the Unknown: 1, 2, 2, 2, 1, 1, 1

    NOT_ENOUGH_VOTES = "Not enough votes" # Gather the Troops
    NO_SPECIFIC_SCENARIO = "No specific scenario" # Await the Signal

    DECIDED = "Decided"

class LevelType(PyEnum):
    LEVEL_1 = (1, 0.98, 100)  # max_prob, min_prob, coins
    LEVEL_2 = (0.98, 0.9, 200)
    LEVEL_3 = (0.9, 0.7, 300)

    def __init__(self, max_prob: float, min_prob: float, coins: int):
        self.max_prob = max_prob
        self.min_prob = min_prob
        self.coins = coins

    @property
    def min_value(self) -> float:
        """Alias for min_prob"""
        return self.min_prob

    @property
    def max_value(self) -> float:
        """Alias for max_prob"""
        return self.max_prob

    @property
    def range(self) -> Tuple[float, float]:
        """Return the probability range for this level."""
        return (self.min_prob, self.max_prob)

    @classmethod
    def get_level(cls, P_max: float) -> 'LevelType':
        """Determine level based on probability."""
        return next(
            (level for level in cls
             if level.min_prob <= P_max < level.max_prob),
            cls.LEVEL_1  # Default case
        )


class BartlePersonaType(PyEnum):
    ACHIEVER = "Achiever"
    EXPLORER = "Explorer"
    SOCIALIZER = "Socializer"
    KILLER = "Killer"

class BartlePersonaDistributionType(PyEnum):
    ACHIEVER_PORTION = 0.4
    EXPLORER_PORTION = 0.2
    SOCIALIZER_PORTION = 0.3
    KILLER_PORTION = 0.1
