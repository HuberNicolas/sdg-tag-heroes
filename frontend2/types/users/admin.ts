import type { UserSchemaBase, UserSchemaFull } from "./user";

export interface AdminSchemaBase {
  adminId: number;
  user?: UserSchemaBase | UserSchemaFull | null;
}

export interface AdminSchemaFull extends AdminSchemaBase {
  createdAt: string;
  updatedAt: string;
}
