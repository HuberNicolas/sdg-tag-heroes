export interface InstituteSchemaBase {
  instituteId: number;
  instituteName: string;
}

export interface InstituteSchemaFull extends InstituteSchemaBase {
  instituteSetSpec: string;
  createdAt: string;
  updatedAt: string;
}
