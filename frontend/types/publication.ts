import type { AuthorSchemaBase, AuthorSchemaFull } from "./author";
import type { SDGLabelSummarySchemaBase, SDGLabelSummarySchemaFull } from "./sdgLabelSummary";
import type { SDGPredictionSchemaBase, SDGPredictionSchemaFull } from "./sdgPrediction";
import type { SDGTargetPredictionSchemaBase, SDGTargetPredictionSchemaFull } from "./sdgTargetPrediction";
import type { DimensionalityReductionSchemaBase } from "./dimensionalityReduction";
import type { PublicationClusterSchemaBase, PublicationClusterSchemaFull } from "./clusters/publicationCluster";
import type { FactSchemaBase, FactSchemaFull } from "./fact";
import type { SummarySchemaBase, SummarySchemaFull } from "./summary";
import type { FacultySchemaBase, FacultySchemaFull } from "./faculty";
import type { InstituteSchemaBase, InstituteSchemaFull } from "./institute";
import type { DivisionSchemaBase, DivisionSchemaFull } from "./division";
import type {CollectionSchemaBase, CollectionSchemaFull} from "./collection";

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

  collectionId?: number | null;
  collection?: CollectionSchemaBase | CollectionSchemaFull | null;
}

export interface PublicationSchemaFull extends PublicationSchemaBase {
  createdAt: string;
  updatedAt: string;
}
