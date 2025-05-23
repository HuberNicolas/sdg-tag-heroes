import { defineStore } from "pinia";
import type {
  SDGLabelSummarySchemaBase,
  SDGLabelSummarySchemaFull,
} from "~/types/sdgLabelSummary";
import useSDGLabelSummaries from "~/composables/useSDGLabelSummaries";

export const useSDGLabelSummariesStore = defineStore("sdgLabelSummaries", {
  state: () => ({
    sdgLabelSummaries: [] as SDGLabelSummarySchemaFull[],
    sdgLabelSummaryDetails: null as SDGLabelSummarySchemaFull | null,
    sdgLabelSummaryForPublication: null as SDGLabelSummarySchemaFull | null,
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    // Fetch all SDG Label Summaries
    async fetchSDGLabelSummaries() {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGLabelSummaries } = useSDGLabelSummaries();
        this.sdgLabelSummaries = await getSDGLabelSummaries();
      } catch (error) {
        this.error = `Failed to fetch SDG Label Summaries: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a single SDG Label Summary by ID
    async fetchSDGLabelSummaryById(labelSummaryId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGLabelSummaryById } = useSDGLabelSummaries();
        this.sdgLabelSummaryDetails = await getSDGLabelSummaryById(labelSummaryId);
      } catch (error) {
        this.error = `Failed to fetch SDG Label Summary: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch SDG Label Summary for a specific publication
    async fetchSDGLabelSummaryByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGLabelSummaryByPublicationId } = useSDGLabelSummaries();
        this.sdgLabelSummaryForPublication = await getSDGLabelSummaryByPublicationId(publicationId);
      } catch (error) {
        this.error = `Failed to fetch SDG Label Summary for publication: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
