export interface PublicationClusterSchemaBase {
  publicationClusterId: number;
  publicationId: number;
  clusterId: number;
  clusterIdString: string;
  sdg?: number | null;
  level?: number | null;
  topic?: number | null;
}

export interface PublicationClusterSchemaFull extends PublicationClusterSchemaBase {
  createdAt: string;
  updatedAt: string;
}
