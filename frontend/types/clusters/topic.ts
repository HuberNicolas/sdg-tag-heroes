import type { PublicationClusterSchemaBase, PublicationClusterSchemaFull } from "./publicationCluster";

export interface ClusterTopicSchemaBase {
  topicId: number;
  levelId: number;
  clusterIdStr: string;
  size: number;
  centerX: number;
  centerY: number;
  name: string;
  topicName: string;
  publications: (PublicationClusterSchemaBase | PublicationClusterSchemaFull)[];
}

export interface ClusterTopicSchemaFull extends ClusterTopicSchemaBase {
  createdAt: string;
  updatedAt: string;
}
