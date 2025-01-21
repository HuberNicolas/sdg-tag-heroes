import { ClusterLevelSchemaBase, ClusterLevelSchemaFull } from "./level";

export interface ClusterGroupSchemaBase {
  id: number;
  name: string;
  clusterLevels: (ClusterLevelSchemaBase | ClusterLevelSchemaFull)[];
}

export interface ClusterGroupSchemaFull extends ClusterGroupSchemaBase {
  createdAt: string;
  updatedAt: string;
}
