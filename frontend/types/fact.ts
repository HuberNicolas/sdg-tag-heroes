export interface FactSchemaBase {
  factId: number;
  content?: string | null;
  publicationId: number;
}

export interface FactSchemaFull extends FactSchemaBase {
  createdAt: string;
  updatedAt: string;
}
