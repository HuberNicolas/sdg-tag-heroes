export interface UserEnrichedSkillsDescription {
  inputSkills: string[];
  enrichedDescription: string;
}

export interface UserEnrichedInterestsDescription {
  inputInterests: string[];
  enrichedDescription: string;
}

export interface SDGPrediction {
  input: string;
  proposedSdgId: number;
  reasoning: string;
}


// REQUESTS
export type UserProfileSkillsRequest = {
  skills: string
};
export type UserProfileInterestsRequest = {
  interests: string
};
