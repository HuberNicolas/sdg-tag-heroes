export interface ExplanationSchema {
  mongodbId: string;
  sqlId: number;
  oaiIdentifier: string;
  inputTokens: string[];
  tokenScores: number[][];
  baseValues: number[];
  xaiMethod: string;
  predictionModel: string;
}
