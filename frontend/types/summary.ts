export interface SummarySchemaBase {
  summaryId: number;
  content?: string | null;
  publicationId: number;
}

export interface SummarySchemaFull extends SummarySchemaBase {
  createdAt: string;
  updatedAt: string;
}
