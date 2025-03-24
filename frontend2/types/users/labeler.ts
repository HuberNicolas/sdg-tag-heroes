import type { UserSchemaBase, UserSchemaFull } from "./user";

export interface LabelerSchemaBase {
  labelerId: number;
  labelerScore: number;
  user?: UserSchemaBase | UserSchemaFull | null;
}

export interface LabelerSchemaFull extends LabelerSchemaBase {
  createdAt: string;
  updatedAt: string;
}
