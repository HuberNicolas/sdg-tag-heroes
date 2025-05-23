import type { DecisionType, ScenarioType } from "./enums";
import type {
  AnnotationSchemaBase,
  AnnotationSchemaFull,
} from "./annotation";

import type {
  SDGUserLabelSchemaBase,
  SDGUserLabelSchemaFull
} from "./sdgUserLabel"

export interface SDGLabelDecisionSchemaBase {
  decisionId: number;
  suggestedLabel: number;
  decidedLabel: number;
  publicationId: number;
  decisionType: DecisionType;
  scenarioType: ScenarioType;
  expertId?: number | null;
  historyId?: number | null;
  comment?: string | null;
  annotations: (AnnotationSchemaBase | AnnotationSchemaFull)[];

}

export interface SDGLabelDecisionSchemaFull extends SDGLabelDecisionSchemaBase {
  createdAt: string;
  updatedAt: string;
}

export interface SDGLabelDecisionSchemaExtended extends SDGLabelDecisionSchemaFull {
  userLabels: SDGUserLabelSchemaFull[]; // Include all user labels attached to the decision
  annotations: AnnotationSchemaFull[];  // Ensure annotations are fully loaded
}
