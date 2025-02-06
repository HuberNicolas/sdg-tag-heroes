import { defineStore } from "pinia";
import type { SDGPredictionSchemaFull } from "~/types/sdgPrediction";
import useSDGPredictions from "~/composables/useSDGPredictions";

export const useSDGPredictionsStore = defineStore("sdgPredictions", {
  state: () => ({
    sdgPredictions: [] as SDGPredictionSchemaFull[],
    sdgPredictionDetails: null as SDGPredictionSchemaFull | null,
    isLoading: false,
    error: null as string | null,
    distributionMetrics: [] as any[],
    publicationMetrics: null as any | null,
    topPublications: [] as any[],

    partitionedSDGPredictions: [] as SDGPredictionSchemaFull[], // All SDGs
    sdgLevelSDGPredictions: [] as SDGPredictionSchemaFull[], // 1 SDG

    scenarioTypeSDGPredictions: [] as SDGPredictionSchemaFull[],


    selectedPartitionedSDGPredictions: [] as SDGPredictionSchemaFull[],
  }),
  actions: {
    // Fetch SDG predictions by IDs
    async fetchSDGPredictionsByIds(predictionIds: number[]) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGPredictionsByIds } = useSDGPredictions();
        this.sdgPredictions = await getSDGPredictionsByIds(predictionIds);
      } catch (error) {
        this.error = `Failed to fetch SDG predictions: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch SDG predictions by publication IDs
    async fetchSDGPredictionsByPublicationIds(publicationIds: number[]) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGPredictionsByPublicationIds } = useSDGPredictions();
        this.sdgPredictions = await getSDGPredictionsByPublicationIds(publicationIds);
      } catch (error) {
        this.error = `Failed to fetch SDG predictions by publication IDs: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch SDG predictions for a single publication ID
    async fetchSDGPredictionsByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGPredictionsByPublicationId } = useSDGPredictions();
        this.sdgPredictionDetails = await getSDGPredictionsByPublicationId(publicationId);
      } catch (error) {
        this.error = `Failed to fetch SDG predictions for publication ID ${publicationId}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch default model SDG predictions for a single publication ID
    async fetchDefaultModelSDGPredictionsByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getDefaultModelSDGPredictionsByPublicationId } = useSDGPredictions();
        this.sdgPredictionDetails = await getDefaultModelSDGPredictionsByPublicationId(publicationId);
      } catch (error) {
        this.error = `Failed to fetch default model SDG predictions for publication ID ${publicationId}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch distribution metrics for a list of publication IDs
    async fetchDistributionMetricsByPublicationIds(publicationIds: number[]) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getDistributionMetricsByPublicationIds } = useSDGPredictions();
        this.distributionMetrics = await getDistributionMetricsByPublicationIds(publicationIds);
      } catch (error) {
        this.error = `Failed to fetch distribution metrics: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch metrics for a single publication ID
    async fetchPublicationMetricsById(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationMetricsById } = useSDGPredictions();
        this.publicationMetrics = await getPublicationMetricsById(publicationId);
      } catch (error) {
        this.error = `Failed to fetch metrics for publication ID ${publicationId}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch top or bottom N publications based on a metric
    async fetchPublicationsByMetric(metricType: string, order: string, topN: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getPublicationsByMetric } = useSDGPredictions();
        this.topPublications = await getPublicationsByMetric(metricType, order, topN);
      } catch (error) {
        this.error = `Failed to fetch publications by metric: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch SDG predictions for a specific part of dimensionality reductions
    async fetchSDGPredictionsForDimensionalityReductionsPartitioned(
      reductionShorthand: string,
      partNumber: number,
      totalParts: number
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGPredictionsForDimensionalityReductionsPartitioned } = useSDGPredictions();
        this.partitionedSDGPredictions = await getSDGPredictionsForDimensionalityReductionsPartitioned(
          reductionShorthand,
          partNumber,
          totalParts
        );
      } catch (error) {
        this.error = `Failed to fetch partitioned SDG predictions: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch SDG predictions by SDG and level
    async fetchSDGPredictionsByLevel(sdg: number, reductionShorthand: string, level: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGPredictionsByLevel } = useSDGPredictions();
        this.sdgLevelSDGPredictions = await getSDGPredictionsByLevel(sdg, reductionShorthand, level);
      } catch (error) {
        this.error = `Failed to fetch SDG predictions for SDG ${sdg}, level ${level}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch SDG predictions by SDG, reduction shorthand, and scenario type
    async fetchSDGPredictionsForDimensionalityReductionsWithScenario(
      sdg: number,
      reductionShorthand: string,
      scenarioType: string
    ) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGPredictionsForDimensionalityReductionsWithScenario } =
          useSDGPredictions();
        this.scenarioTypeSDGPredictions =
          await getSDGPredictionsForDimensionalityReductionsWithScenario(
            sdg,
            reductionShorthand,
            scenarioType
          );
      } catch (error) {
        this.error = `Failed to fetch SDG predictions for SDG ${sdg} and scenario ${scenarioType}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
