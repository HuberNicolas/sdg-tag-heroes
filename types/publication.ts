import { AuthorSchemaBase, AuthorSchemaFull } from "./author";
import { SDGLabelSummarySchemaBase, SDGLabelSummarySchemaFull } from "./sdgLabelSummary";
import { SDGPredictionSchemaBase, SDGPredictionSchemaFull } from "./sdgPrediction";
import { SDGTargetPredictionSchemaBase, SDGTargetPredictionSchemaFull } from "./sdgTargetPrediction";
import { DimensionalityReductionSchemaBase } from "./dimensionalityReduction";
import { PublicationClusterSchemaBase, PublicationClusterSchemaFull } from "./clusters/publicationCluster";
import { FactSchemaBase, FactSchemaFull } from "./fact";
import { SummarySchemaBase, SummarySchemaFull } from "./summary";
import { FacultySchemaBase, FacultySchemaFull } from "./faculty";
import { InstituteSchemaBase, InstituteSchemaFull } from "./institute";
import { DivisionSchemaBase, DivisionSchemaFull } from "./division";

export interface PublicationSchemaBase {
  publicationId: number;
  oaiIdentifier: string;
  oaiIdentifierNum: number;
  title?: string | null;
  description?: string | null;
  publisher?: string | null;
  date?: string | null;
  year?: number | null;
  source?: string | null;
  language?: string | null;
  format?: string | null;
  embedded: boolean;
  setSpec?: string | null;
  isDimReduced: boolean;

  authors?: (AuthorSchemaBase | AuthorSchemaFull)[] | null;
  sdgLabelSummary?: (SDGLabelSummarySchemaBase | SDGLabelSummarySchemaFull)[] | null;
  sdgPredictions?: (SDGPredictionSchemaBase | SDGPredictionSchemaFull)[] | null;
  sdgTargetPredictions?: (SDGTargetPredictionSchemaBase | SDGTargetPredictionSchemaFull)[] | null;
  dimensionalityReductions?: DimensionalityReductionSchemaBase[] | null;

  clusters?: (PublicationClusterSchemaBase | PublicationClusterSchemaFull)[] | null;
  fact?: FactSchemaBase | FactSchemaFull | null;
  summary?: SummarySchemaBase | SummarySchemaFull | null;

  facultyId?: number | null;
  faculty?: (FacultySchemaBase | FacultySchemaFull)[] | null;
  instituteId?: number | null;
  institute?: (InstituteSchemaBase | InstituteSchemaFull)[] | null;
  divisionId?: number | null;
  division?: (DivisionSchemaBase | DivisionSchemaFull)[] | null;
}

export interface PublicationSchemaFull extends PublicationSchemaBase {
  createdAt: string;
  updatedAt: string;
}
