import type { SDGTargetSchemaBase, SDGTargetSchemaFull } from "./target";

export interface SDGGoalSchemaBase {
  id: number;
  index: number;
  name: string;
  color: string;
  icon?: string | null;
  shortTitle: string;
  keywords: string;
  explanation: string;
  sdgTargets?: (SDGTargetSchemaBase | SDGTargetSchemaFull)[];
}

export interface SDGGoalSchemaFull extends SDGGoalSchemaBase {
  createdAt: string;
  updatedAt: string;
}
