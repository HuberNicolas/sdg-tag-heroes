import { defineStore } from "pinia";
import type {
  PublicationSchemaBase,
  PublicationSchemaFull,
  PublicationSimilaritySchema,
  PublicationSDGAnalysisSchema,
  PublicationKeywordsSchema,
  FactSchemaFull,
  PublicationSummarySchema,
  PublicationsCollectiveSummarySchema,
} from "~/types/publications";
import usePublications from "~/composables/usePublications";

export const usePublicationsStore = defineStore("publications", {
  state: () => ({
    publications: [] as PublicationSchemaBase[],
    publicationDetails: null as PublicationSchemaFull | null,
    similarPublications: null as PublicationSimilaritySchema | null,
    sdgAnalysis: null as PublicationSDGAnalysisSchema | null,
    keywords: null as PublicationKeywordsSchema | null,
    fact: null as FactSchemaFull | null,
    summary: null as PublicationSummarySchema | null,
    collectiveSummary: null as PublicationsCollectiveSummarySchema | null,
    partitionedPublications: [] as PublicationSchemaBase[],
    isLoading: false,
    error: null as string | null,
  }),
  getters: {
    // Example getter for filtered publications
    filteredPublications: (state) => (searchTerm: string) => {
      return state.publications.filter((pub) =>
        pub.title?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    },
  },
  actions: {
    // Fetch publications by IDs
    async fetchPublicationsByIds(publicationIds: number[]) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationsByIds } = usePublications();
        this.publications = await getPublicationsByIds(publicationIds);
      } catch (error) {
        this.error = `Failed to fetch publications: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a single publication by ID
    async fetchPublicationById(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationById } = usePublications();
        this.publicationDetails = await getPublicationById(publicationId);
      } catch (error) {
        this.error = `Failed to fetch publication: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch similar publications
    async fetchSimilarPublications(
      topK: number,
      userQuery: string,
      publicationIds: number[]
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSimilarPublications } = usePublications();
        this.similarPublications = await getSimilarPublications(
          topK,
          userQuery,
          publicationIds
        );
      } catch (error) {
        this.error = `Failed to fetch similar publications: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch SDG analysis for a publication
    async fetchPublicationSDGAnalysis(publicationId: number, sdgId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationSDGAnalysis } = usePublications();
        this.sdgAnalysis = await getPublicationSDGAnalysis(
          publicationId,
          sdgId
        );
      } catch (error) {
        this.error = `Failed to fetch SDG analysis: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch keywords for a publication
    async fetchPublicationKeywords(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationKeywords } = usePublications();
        this.keywords = await getPublicationKeywords(publicationId);
      } catch (error) {
        this.error = `Failed to fetch keywords: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a "Did You Know" fact for a publication
    async fetchPublicationFact(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationFact } = usePublications();
        this.fact = await getPublicationFact(publicationId);
      } catch (error) {
        this.error = `Failed to fetch fact: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a summary for a publication
    async fetchPublicationSummary(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationSummary } = usePublications();
        this.summary = await getPublicationSummary(publicationId);
      } catch (error) {
        this.error = `Failed to fetch summary: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a collective summary for multiple publications
    async fetchCollectiveSummary(publicationIds: number[]) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getCollectiveSummary } = usePublications();
        this.collectiveSummary = await getCollectiveSummary(publicationIds);
      } catch (error) {
        this.error = `Failed to fetch collective summary: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch publications for a specific part of dimensionality reductions
    async fetchPublicationsForDimensionalityReductionsPartitioned(
      reductionShorthand: string,
      partNumber: number,
      totalParts: number
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationsForDimensionalityReductionsPartitioned } = usePublications();
        this.partitionedPublications = await getPublicationsForDimensionalityReductionsPartitioned(
          reductionShorthand,
          partNumber,
          totalParts
        );
      } catch (error) {
        this.error = `Failed to fetch publications for partitioned dimensionality reductions: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
