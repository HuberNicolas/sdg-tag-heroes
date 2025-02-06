import { defineStore } from "pinia";
import type {
  DimensionalityReductionSchemaFull,
  FilteredDimensionalityReductionStatisticsSchema,
  GroupedDimensionalityReductionResponseSchema,
  UserCoordinatesSchema,
} from "~/types/dimensionalityReductions";
import useDimensionalityReductions from "~/composables/useDimensionalityReductions";

export const useDimensionalityReductionsStore = defineStore("dimensionalityReductions", {
  state: () => ({
    dimensionalityReductions: [] as DimensionalityReductionSchemaFull[],
    filteredReductions: null as FilteredDimensionalityReductionStatisticsSchema | null,
    groupedReductions: null as GroupedDimensionalityReductionResponseSchema | null,
    userCoordinates: null as UserCoordinatesSchema | null,

    partitionedReductions: [] as DimensionalityReductionSchemaFull[], // All SDGs
    sdgLevelReductions: [] as DimensionalityReductionSchemaFull[], // 1 SDG

    scenarioTypeReductions: [] as DimensionalityReductionSchemaFull[],

    selectedPartitionedReductions: [] as DimensionalityReductionSchemaFull[],
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    // Fetch all dimensionality reductions
    async fetchDimensionalityReductions() {
      this.isLoading = true;
      this.error = null;

      try {
        const { getDimensionalityReductions } = useDimensionalityReductions();
        this.dimensionalityReductions = await getDimensionalityReductions();
      } catch (error) {
        this.error = `Failed to fetch dimensionality reductions: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch dimensionality reductions for specific publications
    async fetchDimensionalityReductionsForPublications(
      request: DimensionalityReductionPublicationIdsRequest,
      reductionShorthand: string = "UMAP-15-0.0-2"
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getDimensionalityReductionsForPublications } = useDimensionalityReductions();
        this.dimensionalityReductions = await getDimensionalityReductionsForPublications(request, reductionShorthand);
      } catch (error) {
        this.error = `Failed to fetch dimensionality reductions for publications: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch filtered dimensionality reductions by SDG range
    async fetchFilteredDimensionalityReductions(
      sdgRange: [number, number],
      limit: number = 10,
      sdgs?: number[],
      model?: string,
      level?: number[],
      reductionShorthand?: string
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getFilteredDimensionalityReductions } = useDimensionalityReductions();
        this.filteredReductions = await getFilteredDimensionalityReductions(
          sdgRange,
          limit,
          sdgs,
          model,
          level,
          reductionShorthand
        );
      } catch (error) {
        this.error = `Failed to fetch filtered dimensionality reductions: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Calculate user coordinates for dimensionality reduction
    async calculateUserCoordinates(request: UserCoordinatesRequest) {
      this.isLoading = true;
      this.error = null;

      try {
        const { calculateUserCoordinates } = useDimensionalityReductions();
        this.userCoordinates = await calculateUserCoordinates(request);
      } catch (error) {
        this.error = `Failed to calculate user coordinates: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a specific part of dimensionality reductions
    async fetchDimensionalityReductionsPartitioned(
      reductionShorthand: string,
      partNumber: number,
      totalParts: number
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getDimensionalityReductionsPartitioned } = useDimensionalityReductions();
        this.partitionedReductions = await getDimensionalityReductionsPartitioned(
          reductionShorthand,
          partNumber,
          totalParts
        );
      } catch (error) {
        this.error = `Failed to fetch partitioned dimensionality reductions: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch dimensionality reductions by SDG and level
    async fetchDimensionalityReductionsBySDGAndLevel(
      sdg: number,
      reductionShorthand: string,
      level: number
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGPredictionsByLevel } = useDimensionalityReductions();
        this.sdgLevelReductions = await getSDGPredictionsByLevel(sdg, reductionShorthand, level);
      } catch (error) {
        this.error = `Failed to fetch dimensionality reductions for SDG ${sdg}, level ${level}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch dimensionality reductions by SDG and scenario type
    async fetchDimensionalityReductionsBySDGAndScenario(
      sdg: number,
      reductionShorthand: string,
      scenarioType: string
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getDimensionalityReductionsBySDGAndScenario } = useDimensionalityReductions();
        this.scenarioTypeReductions = await getDimensionalityReductionsBySDGAndScenario(
          sdg,
          reductionShorthand,
          scenarioType
        );
      } catch (error) {
        this.error = `Failed to fetch dimensionality reductions for SDG ${sdg} and scenario ${scenarioType}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

  },
});
