/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

// SDGGoalSchema
export interface SDGGoalSchemaBase {
  id: number;
  index: number;
  name: string;
  color: string;
  icon?: string | null;
  sdg_targets?: (SDGTargetSchemaBase | SDGTargetSchemaFull)[]; // Nested relationship
}

export interface SDGGoalSchemaFull extends SDGGoalSchemaBase {
  created_at: string;
  updated_at: string;
}

// SDGTargetSchema
export interface SDGTargetSchemaBase {
  id: number;
  index: string;
  text: string;
  color: string;
  target_vector_index: number;
  icon?: string | null;
  sdg_goal?: SDGGoalSchemaBase | SDGGoalSchemaFull; // Nested relationship
}

export interface SDGTargetSchemaFull extends SDGTargetSchemaBase {
  created_at: string;
  updated_at: string;
}
