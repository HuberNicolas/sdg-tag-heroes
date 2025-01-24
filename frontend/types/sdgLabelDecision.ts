import { DecisionType } from "../enums/enums";
import {
  AnnotationSchemaBase,
  AnnotationSchemaFull,
} from "./annotation";

export interface SDGLabelDecisionSchemaBase {
  decisionId: number;
  suggestedLabel: number;
  decidedLabel: number;
  decisionType: DecisionType;
  expertId?: number | null;
  historyId?: number | null;
  comment?: string | null;
  annotations: (AnnotationSchemaBase | AnnotationSchemaFull)[];
}

export interface SDGLabelDecisionSchemaFull extends SDGLabelDecisionSchemaBase {
  createdAt: string;
  updatedAt: string;
}
