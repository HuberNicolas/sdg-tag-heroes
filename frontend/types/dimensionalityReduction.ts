/**
 * Dimensionality Reduction Models
 */

export interface DimensionalityReduction extends BaseEntity, Coordinates {
  dim_red_id: number;
  publication_id: number;
  reduction_technique: string;
  reduction_shorthand: string;
  sdg: number;
  level: number;
}

export interface DimensionalityReductionLevel {
  reductions: DimensionalityReduction[];
}

export interface DimensionalityReductionSDG {
  levels: Record<number, DimensionalityReductionLevel>;
  stats: SDGStatistics | null;
}

/**
 * Statistics Models
 */

export interface SDGStatistics {
  total_levels: number;
  total_reductions: number;
}

export interface DimensionalityReductionStats {
  total_sdg_groups: number;
  total_levels: number;
  total_reductions: number;
  sdg_breakdown: Record<string, SDGStatistics>;
}

/**
 * Response Types
 */

export interface DimensionalityReductionGroupedResponse {
  reductions: Record<string, Record<string, DimensionalityReduction[]>>; // SDG -> Levels -> Reductions
  stats: DimensionalityReductionStats;
}
