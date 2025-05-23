import type { ClusterTopicSchemaBase, ClusterTopicSchemaFull } from "./topic";

export interface ClusterLevelSchemaBase {
  id: number;
  clusterGroupId: number;
  levelNumber: number;
  clusterTopics: (ClusterTopicSchemaBase | ClusterTopicSchemaFull)[];
}

export interface ClusterLevelSchemaFull extends ClusterLevelSchemaBase {
  createdAt: string;
  updatedAt: string;
}
