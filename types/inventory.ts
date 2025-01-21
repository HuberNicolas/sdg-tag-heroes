import { AchievementSchemaBase, AchievementSchemaFull } from "./achievement";

export interface InventorySchemaBase {
  inventoryId: number;
  userId: number;
  achievements: (AchievementSchemaBase | AchievementSchemaFull)[];
}

export interface InventorySchemaFull extends InventorySchemaBase {
  createdAt: string;
  updatedAt: string;
}
