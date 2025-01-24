import type { SDGTargetSchemaBase, SDGTargetSchemaFull } from "./target";

export interface SDGGoalSchemaBase {
  id: number;
  index: number;
  name: string;
  color: string;
  icon?: string | null;
  sdgTargets?: (SDGTargetSchemaBase | SDGTargetSchemaFull)[];
}

export interface SDGGoalSchemaFull extends SDGGoalSchemaBase {
  createdAt: string;
  updatedAt: string;
}
