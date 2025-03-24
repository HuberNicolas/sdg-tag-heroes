import { defineStore } from "pinia";
import type { SDGUserLabelSchemaFull } from "~/types/sdgUserLabel";
import useUserLabels from "~/composables/useUserLabels";

export const useUserLabelsStore = defineStore("userLabels", {
  state: () => ({
    userLabels: [] as SDGUserLabelSchemaFull[],
    isLoading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchUserLabelsByUserId(userId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGUserLabelsByUserId } = useUserLabels();
        this.userLabels = await getSDGUserLabelsByUserId(userId);
      } catch (error) {
        this.error = `Failed to fetch user labels for user ${userId}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
