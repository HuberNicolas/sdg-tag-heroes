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

// REQUESTS
export interface AnnotationCreateRequest {
  user_id: number; // ID of the user creating the annotation
  passage: string; // The passage being annotated
  sdg_user_label_id?: number | null; // Optional link to SDGUserLabel
  decision_id?: number | null; // Optional link to an SDGLabelDecision
  labeler_score: number; // Score assigned by the user
  comment?: string; // Optional comment
}

