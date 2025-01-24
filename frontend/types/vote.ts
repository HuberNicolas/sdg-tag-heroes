import { VoteType } from "../enums/enums";

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
