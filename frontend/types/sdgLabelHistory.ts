export interface SDGLabelHistorySchemaBase {
  historyId: number;
  active: boolean;
}

export interface SDGLabelHistorySchemaFull extends SDGLabelHistorySchemaBase {
  createdAt: string;
  updatedAt: string;
}
