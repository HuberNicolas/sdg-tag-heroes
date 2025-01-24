export interface InventoryAchievementAssociationSchemaBase {
  id: number;
  inventoryId: number;
  achievementId: number;
  comment?: string | null;
  addedAt: string; // ISO date string
}

export interface InventoryAchievementAssociationSchemaFull extends InventoryAchievementAssociationSchemaBase {
  createdAt: string;
  updatedAt: string;
}
