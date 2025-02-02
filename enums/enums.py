from enum import Enum as PyEnum

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

class LevelType(PyEnum):
    LEVEL_1 = (1, 0.98)  # Level 1
    LEVEL_2 = (0.98, 0.9)  # Level 2
    LEVEL_3 = (0.9, 0.7)  # Level 3

    @property
    def max_value(self):
        return self.value[0]

    @property
    def min_value(self):
        return self.value[1]
