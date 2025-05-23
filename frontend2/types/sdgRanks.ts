export interface SDGRankSchemaBase {
  rankId: number;
  sdgGoalId: number;
  tier: number;
  name: string;
  description?: string | null;
  xpRequired: number;
}

export interface SDGRankSchemaFull extends SDGRankSchemaBase {
  createdAt: string;
  updatedAt: string;
}



// Not derived from model
export interface UserSDGRankSchemaFull {
  userId: number;
  ranks: SDGRankSchemaFull[]; // User-specific ranks
}



// REQUESTS
export interface SDGRankCreateRequest {
  sdgGoalId: number;  // ID of the SDG goal (1-17)
  tier: number;  // Rank tier (1, 2, 3)
  name: string;  // Rank name
  description?: string;  // Optional description
  xpRequired: number;  // XP required for this rank
}
