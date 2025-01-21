export interface SDGTargetPredictionSchemaBase {
  targetPredictionId: number;
  publicationId: number;
  predictionModel: string;
  predicted: boolean;
  lastPredictedTarget: string;
  targetPredictions: Record<string, number>; // Key-value pairs for 168 targets
}

export interface SDGTargetPredictionSchemaFull extends SDGTargetPredictionSchemaBase {
  createdAt: string;
  updatedAt: string;
}
