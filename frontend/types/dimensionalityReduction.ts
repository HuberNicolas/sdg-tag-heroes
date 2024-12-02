export interface DimensionalityReduction {
  dim_red_id: number;
  publication_id: number;
  reduction_technique: string;
  reduction_shorthand: string;
  x_coord: number;
  y_coord: number;
  z_coord: number;
  sdg: number;
  level: number;
  created_at: string;
  updated_at: string;
}

export interface DimensionalityReductionResponse {
  reductions: Record<string, Record<string, DimensionalityReduction[]>>; // SDG -> Levels -> Reductions
  stats: {
    total_sdg_groups: number;
    total_levels: number;
    total_reductions: number;
    sdg_breakdown: Record<
      string,
      {
        total_levels: number;
        total_reductions: number;
      }
    >;
  };
}
