import type { UserSchemaBase, UserSchemaFull } from "./user";

export interface GroupSchemaBase {
  groupId: number;
  name: string;
  members: (UserSchemaBase | UserSchemaFull)[];
}

export interface GroupSchemaFull extends GroupSchemaBase {
  createdAt: string;
  updatedAt: string;
}
