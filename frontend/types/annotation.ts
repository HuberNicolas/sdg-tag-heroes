import type { VoteSchemaBase, VoteSchemaFull } from "./vote";

export interface AnnotationSchemaBase {
  annotationId: number;
  userId: number;
  sdgUserLabelId?: number | null;
  decisionId?: number | null;
  labelerScore: number;
  comment: string;
  votes: (VoteSchemaBase | VoteSchemaFull)[];
}

export interface AnnotationSchemaFull extends AnnotationSchemaBase {
  createdAt: string;
  updatedAt: string;
}
