export interface DimensionalityReductionSchemaBase {
  dimRedId: number;
  publicationId: number;
  reductionTechnique?: string | null;
  reductionShorthand?: string | null;
  sdg: number;
  level: number;
  xCoord: number;
  yCoord: number;
  zCoord?: number | null;
  reductionDetails?: string | null;
}

export interface DimensionalityReductionSchemaFull extends DimensionalityReductionSchemaBase {
  createdAt: string;
  updatedAt: string;
}
