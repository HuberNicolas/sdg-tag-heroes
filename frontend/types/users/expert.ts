import { UserSchemaBase, UserSchemaFull } from "./user";

export interface ExpertSchemaBase {
  expertId: number;
  expertScore: number;
  user?: UserSchemaBase | UserSchemaFull | null;
}

export interface ExpertSchemaFull extends ExpertSchemaBase {
  createdAt: string;
  updatedAt: string;
}
