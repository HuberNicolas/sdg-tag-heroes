export interface CollectionSchemaBase {
  collectionId: number;
  count: number;
  name: string;
  shortName: string;
  representation: string[]; // JSON parsed into an array of strings
  aspect1: string[];
  aspect2: string[];
  aspect3: string[];
}

export interface CollectionSchemaFull extends CollectionSchemaBase {
  createdAt: string;
  updatedAt: string;
}
