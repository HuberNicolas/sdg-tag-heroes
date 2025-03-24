export interface DivisionSchemaBase {
  divisionId: number;
  divisionName: string;
}

export interface DivisionSchemaFull extends DivisionSchemaBase {
  divisionSetSpec: string;
  createdAt: string;
  updatedAt: string;
}
