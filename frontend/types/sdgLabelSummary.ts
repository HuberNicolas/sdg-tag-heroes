export interface SDGLabelSummarySchemaBase {
  sdgLabelSummaryId: number;
  publicationId: number;
  historyId: number;
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
}

export interface SDGLabelSummarySchemaFull extends SDGLabelSummarySchemaBase {
  createdAt: string;
  updatedAt: string;
}
