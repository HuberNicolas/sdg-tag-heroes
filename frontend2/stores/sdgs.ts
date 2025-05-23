import { defineStore } from "pinia";
import type {
  SDGGoalSchemaFull,
} from "~/types/sdgs/goal";
import useSDGs from "~/composables/useSDGs";

export const useSDGsStore = defineStore("sdgs", {
  state: () => ({
    sdgs: [] as SDGGoalSchemaFull[],
    sdgDetails: null as SDGGoalSchemaFull | null,
    selectedSDG: 0, // 0: no SDG selected
    selectedSDGLabel: 0,
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    setSelectedSDG(selectedSDG: number) {
      this.selectedSDG = selectedSDG;
    },

    setSelectedSDGLabel(selectedSDGLabel: number) {
      this.selectedSDGLabel = selectedSDGLabel;
    },

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

    getColorBySDG(sdgId: number) {
      const sdg = this.sdgs.find((goal) => goal.id === sdgId);
      return sdg ? sdg.color : null;
    },
  },
  getters: {
    getSelectedSDG(state) {
      return state.selectedSDG;
    },
    getSelectedSDGLabel(state) {
      return state.selectedSDGLabel;
    },
    getShortTitleBySDG: (state) => (sdgId: number) => {
      const sdg = state.sdgs.find((goal) => goal.id === sdgId);
      return sdg ? sdg.shortTitle : "Unknown";
    },
  },
});
