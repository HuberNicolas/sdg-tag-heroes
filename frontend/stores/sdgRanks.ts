import { defineStore } from "pinia";
import type { SDGRankSchemaFull, UserSDGRankSchemaFull } from "~/types/sdgRanks";
import useSDGRanks from "~/composables/useSDGRanks";

export const useSDGRanksStore = defineStore("sdgRanks", {
  state: () => ({
    sdgRanks: [] as SDGRankSchemaFull[],
    userSDGRanks: [] as UserSDGRankSchemaFull[], // Ranks per user


    userSDGRank: null as SDGRankSchemaFull | null, // Personal Rank
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    // Fetch all SDG ranks for Users
    async fetchSDGRanks() {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGRanks } = useSDGRanks();
        this.sdgRanks = await getSDGRanks();
      } catch (error) {
        this.error = `Failed to fetch SDG ranks: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },


    // Fetch all SDG ranks for Users
    async fetchSDGRanksForUsers() {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGRanksForUsers } = useSDGRanks();
        this.userSDGRanks = await getSDGRanksForUsers();
      } catch (error) {
        this.error = `Failed to fetch SDG ranks: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a single SDG rank by ID
    async fetchSDGRankByUserId(userId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGRankByUserId } = useSDGRanks();
        this.userSDGRank = await getSDGRankByUserId(userId);
      } catch (error) {
        this.error = `Failed to fetch SDG rank: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
  getters: {
    // Dynamically generate sdgLevels from the fetched SDG ranks
    sdgLevels: (state) => {
      const levels: Record<string, Record<string, { name: string; description: string; xp_required: number }>> = {};

      state.sdgRanks.forEach((rank) => {
        const sdgKey = `sdg_${rank.sdgGoalId}`;
        const tierKey = `tier_${rank.tier}`;

        if (!levels[sdgKey]) {
          levels[sdgKey] = {};
        }

        levels[sdgKey][tierKey] = {
          name: rank.name,
          description: rank.description || "",
          xp_required: rank.xpRequired,
        };
      });

      return levels;
    },
  },
});
