import { defineStore } from "pinia";
import type { ExplanationSchema } from "~/types/explanation";
import useExplanations from "~/composables/useExplanations";

export const useExplanationsStore = defineStore("explanations", {
  state: () => ({
    explanation: null as ExplanationSchema | null,
    isLoading: false,
    error: null as string | null,
    markedText: "" as string,
    comment: "" as string,
    showShap: true,
  }),
  getters: {
    explanationDetails: (state) => state.explanation,
  },
  actions: {
    // Fetch explanation by publication ID
    async fetchExplanationByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getExplanationByPublicationId } = useExplanations();
        this.explanation = await getExplanationByPublicationId(publicationId);
      } catch (error) {
        this.error = `Failed to fetch explanation: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Action to update the marked text
    setMarkedText(text: string) {
      this.markedText = text;
    },

    // Action to update the comment
    setComment(text: string) {
      this.comment = text;
    },

    setShowShap(showShap: boolean) {
      this.showShap = showShap;
    }
  },
});
