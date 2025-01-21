import {
  InventoryAchievementAssociationSchemaBase,
  InventoryAchievementAssociationSchemaFull,
} from "./inventoryAchievementAssociation";

export interface AchievementSchemaBase {
  achievementId: number;
  name: string;
  description?: string | null;
  inventoryAchievements: (
    | InventoryAchievementAssociationSchemaBase
    | InventoryAchievementAssociationSchemaFull
  )[];
}

export interface AchievementSchemaFull extends AchievementSchemaBase {
  createdAt: string;
  updatedAt: string;
}
