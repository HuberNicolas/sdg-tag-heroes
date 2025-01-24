import { defineStore } from "pinia";
import type {
  SDGGoalSchemaFull,
} from "~/types/sdgs";
import useSDGs from "~/composables/useSDGs";

export const useSDGsStore = defineStore("sdgs", {
  state: () => ({
    sdgs: [] as SDGGoalSchemaFull[],
    sdgDetails: null as SDGGoalSchemaFull | null,
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    // Fetch all SDGs
    async fetchSDGs() {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGs } = useSDGs();
        this.sdgs = await getSDGs();
      } catch (error) {
        this.error = `Failed to fetch SDGs: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a single SDG by ID
    async fetchSDGById(sdgId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGById } = useSDGs();
        this.sdgDetails = await getSDGById(sdgId);
      } catch (error) {
        this.error = `Failed to fetch SDG: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
