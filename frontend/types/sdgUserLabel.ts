import type {
  AnnotationSchemaBase,
  AnnotationSchemaFull,
} from "./annotation";
import type { VoteSchemaBase, VoteSchemaFull } from "./vote";
import type {
  SDGLabelDecisionSchemaBase,
  SDGLabelDecisionSchemaFull,
} from "./sdgLabelDecision";

export interface SDGUserLabelSchemaBase {
  labelId: number;
  userId: number;
  publicationId: number;
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


// Not derived from model
export interface SDGUserLabelsCommentSummarySchema {
  userLabelsIds: number[];
  summary: string;
}


// REQUESTS
export interface UserLabelRequest {
  user_id: number; // The user creating the label
  vote_label: number; // The SDG label voted by the user
  abstract_section?: string; // Optional abstract section
  comment?: string; // Optional comment
  decision_id?: number | null; // Link to an existing decision (optional)
  publication_id?: number | null; // Link to a publication (optional)
  decision_type?: string; // Default decision type (e.g., "CONSENSUS_MAJORITY")
}

