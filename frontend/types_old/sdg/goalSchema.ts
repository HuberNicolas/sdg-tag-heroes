import type { SDGTarget } from "~/types/sdg/targetSchema";

export interface SDGGoal {
  id: number;
  index: number;
  name: string;
  color: string;
  icon?: string;
  sdg_targets?: SDGTarget[];
}
