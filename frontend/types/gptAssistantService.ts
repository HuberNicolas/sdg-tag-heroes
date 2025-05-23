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

export interface UserCoordinates {
  x_coord: number;
  y_coord: number;
  z_coord?: number; // Optional, default to 0.0 if not provided
  embedding_time: number;
  model_loading_time: number;
  umap_reduction_transform_time: number;
}




// REQUESTS
export type UserProfileSkillsRequest = {
  skills: string
};
export type UserProfileInterestsRequest = {
  interests: string
};
export type UserCoordinatesRequest = {
  sdg: number;
  level: number;
  userQuery: string;
};
