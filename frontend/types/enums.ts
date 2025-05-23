export enum UserRole {
  USER = "user",
  ADMIN = "admin",
  LABELER = "labeler",
  EXPERT = "expert",
}

export enum DecisionType {
  CONSENSUS_MAJORITY = "Consensus Majority",
  CONSENSUS_TECHNOCRATIC = "Consensus Technocratic",
  EXPERT_DECISION = "Expert Decision",
}

export enum VoteType {
  POSITIVE = "positive",
  NEUTRAL = "neutral",
  NEGATIVE = "negative",
}


export enum SDGType {
  SDG_1 = "sdg1",
  SDG_2 = "sdg2",
  SDG_3 = "sdg3",
  SDG_4 = "sdg4",
  SDG_5 = "sdg5",
  SDG_6 = "sdg6",
  SDG_7 = "sdg7",
  SDG_8 = "sdg8",
  SDG_9 = "sdg9",
  SDG_10 = "sdg10",
  SDG_11 = "sdg11",
  SDG_12 = "sdg12",
  SDG_13 = "sdg13",
  SDG_14 = "sdg14",
  SDG_15 = "sdg15",
  SDG_16 = "sdg16",
  SDG_17 = "sdg17",

  // In sdg_label decision:
  SDG_0 = "sdg0",  // not defined
  SDG_18 = "sdg18" // zero class
}

export enum ScenarioType {
  CONFIRM = "Confirm", // Crown the Champion: 6, 4
  TIEBREAKER = "Tiebreaker", // Tip the Scales: 5, 5
  INVESTIGATE = "Investigate", // Unravel the Mystery: 3, 3, 3, 1
  EXPLORE = "Explore", // Chart the Unknown: 1, 2, 2, 2, 1, 1, 1

  SCARCE_LABELS = "Scarce Labels", // Few annotations available
  HIGH_UNCERTAINTY = "High Uncertainty", // High entropy cases

  NOT_ENOUGH_VOTES = "Not enough votes", // Gather the Troops
  NO_SPECIFIC_SCENARIO = "No specific scenario", // Await the Signal

  DECIDED = "Decided"
}

export enum Quadrant {
  ONE_PUB_ONE_SDG = "1 Publication, 1 SDG",
  ONE_PUB_ALL_SDG = "1 Publication, all SDGs",
  MANY_PUBS_ONE_SDG = "Many Publications, 1 SDG",
  MANY_PUBS_ALL_SDG = "Many Publications, all SDGs"
}

export enum Stage {
  PREPARATION = "Preparation",
  EXPLORING = "Exploring",
  LABELING = "Labeling",
  VOTING = "Voting"
}
