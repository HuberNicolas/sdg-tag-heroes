export interface SDGTargetSchemaBase {
  id: number;
  index: string;
  text: string;
  color: string;
  targetVectorIndex: number;
  icon?: string | null;
}

export interface SDGTargetSchemaFull extends SDGTargetSchemaBase {
  createdAt: string;
  updatedAt: string;
}
