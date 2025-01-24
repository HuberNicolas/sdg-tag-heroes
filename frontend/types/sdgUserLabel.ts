import {
  AnnotationSchemaBase,
  AnnotationSchemaFull,
} from "./annotation";
import { VoteSchemaBase, VoteSchemaFull } from "./vote";
import {
  SDGLabelDecisionSchemaBase,
  SDGLabelDecisionSchemaFull,
} from "./sdgLabelDecision";

export interface SDGUserLabelSchemaBase {
  labelId: number;
  userId: number;
  proposedLabel?: number | null;
  votedLabel: number;
  abstractSection?: string | null;
  comment?: string | null;
  annotations: (AnnotationSchemaBase | AnnotationSchemaFull)[];
  votes: (VoteSchemaBase | VoteSchemaFull)[];
  labelDecisions: (SDGLabelDecisionSchemaBase | SDGLabelDecisionSchemaFull)[];
}

export interface SDGUserLabelSchemaFull extends SDGUserLabelSchemaBase {
  createdAt: string;
  updatedAt: string;
}
