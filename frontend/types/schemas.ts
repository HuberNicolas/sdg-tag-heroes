// Author Interfaces
export interface AuthorSchemaBase {
  author_id: number;
  name: string;
  lastname: string;
  surname: string;
  orcid_id?: string | null;
}

export interface AuthorSchemaFull extends AuthorSchemaBase {
  created_at: string;
  updated_at: string;
}

// SDG Prediction Interfaces
export interface SDGPredictionSchemaBase {
  sdg1?: string;
  sdg2?: string;
  sdg3?: string;
  sdg4?: string;
  sdg5?: string;
  sdg6?: string;
  sdg7?: string;
  sdg8?: string;
  sdg9?: string;
  sdg10?: string;
  sdg11?: string;
  sdg12?: string;
  sdg13?: string;
  sdg14?: string;
  sdg15?: string;
  sdg16?: string;
  sdg17?: string;
  predicted: boolean;
  last_predicted_goal: number;
}

export interface SDGPredictionSchemaFull extends SDGPredictionSchemaBase {
  publication_id: number;
  created_at: string;
  updated_at: string;
}

// Faculty, Institute, Division, and DimRed Interfaces
export interface FacultySchemaBase {
  faculty_id: number;
}

export interface FacultySchemaFull extends FacultySchemaBase {
  name: string;
}

export interface InstituteSchemaBase {
  institute_id: number;
}

export interface InstituteSchemaFull extends InstituteSchemaBase {
  name: string;
}

export interface DivisionSchemaBase {
  division_id: number;
}

export interface DivisionSchemaFull extends DivisionSchemaBase {
  name: string;
}

export interface DimRedSchemaBase {
  dim_red_id: number;
  reduction_shorthand: string;
  x_coord: number;
  y_coord: number;
  z_coord: number;
}

export interface DimRedSchemaFull extends DimRedSchemaBase {
  description: string;
}

// Main Publication Interface
export interface PublicationSchema {
  publication_id: number;
  oai_identifier: string;
  oai_identifier_num: number;
  title?: string;
  description?: string;
  authors?: (AuthorSchemaBase | AuthorSchemaFull)[];
  publisher?: string;
  date?: string;
  year?: number;
  source?: string;
  language?: string;
  format?: string;
  sdg_predictions?: SDGPredictionSchemaBase | SDGPredictionSchemaFull;
  embedded: boolean;
  set_spec?: string;
  faculty?: FacultySchemaBase | FacultySchemaFull;
  institute?: InstituteSchemaBase | InstituteSchemaFull;
  division?: DivisionSchemaBase | DivisionSchemaFull;
  dim_red?: DimRedSchemaBase | DimRedSchemaFull;
  dimreduced: boolean;
  created_at: string;
  updated_at: string;
}

export interface SDGGoal {
  id: number;
  index: number;
  name: string;
  color: string;
  icon?: string; // Optional icon field
}
