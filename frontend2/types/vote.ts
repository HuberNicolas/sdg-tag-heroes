import { VoteType } from "./enums";

export interface VoteSchemaBase {
  voteId: number;
  userId: number;
  sdgUserLabelId?: number | null;
  annotationId?: number | null;
  voteType: VoteType;
  score: number;
}

export interface VoteSchemaFull extends VoteSchemaBase {
  createdAt: string;
  updatedAt: string;
}


// Not derived from types
export interface VoteCreateSchema {
  user_id: number;
  sdg_user_label_id?: number | null;
  annotation_id?: number | null;
  vote_type: VoteType;
  score: number;
}
