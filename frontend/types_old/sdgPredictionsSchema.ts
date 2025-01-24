// Define the base schema for an SDG prediction
export interface SDGPredictionSchemaBase {
  prediction_id: number;
  publication_id: number;
  prediction_model: string;
  sdg1: number;
  sdg2: number;
  sdg3: number;
  sdg4: number;
  sdg5: number;
  sdg6: number;
  sdg7: number;
  sdg8: number;
  sdg9: number;
  sdg10: number;
  sdg11: number;
  sdg12: number;
  sdg13: number;
  sdg14: number;
  sdg15: number;
  sdg16: number;
  sdg17: number;
  predicted: boolean;
}

// Extend the base schema for a full SDG prediction
export interface SDGPredictionSchemaFull extends SDGPredictionSchemaBase {
  last_predicted_goal: number;
  created_at: string;
  updated_at: string;
}
