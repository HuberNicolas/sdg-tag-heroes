import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "~/utils/snakeToCamel";
import type { SDGPredictionSchemaFull } from "~/types/sdgPrediction";

export default function useSDGPredictions() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch SDG predictions by IDs
  async function getSDGPredictionsByIds(predictionIds: number[]): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(`${config.public.apiUrl}/sdg-predictions`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
        body: {
          sdg_predictions_ids: predictionIds,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG predictions: ${error}`);
    }
  }

  // Fetch SDG predictions by publication IDs
  async function getSDGPredictionsByPublicationIds(publicationIds: number[]): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(`${config.public.apiUrl}/sdg-predictions/publications`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
        body: {
          publications_ids: publicationIds,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG predictions by publication IDs: ${error}`);
    }
  }

  // Fetch SDG predictions for a single publication ID
  async function getSDGPredictionsByPublicationId(publicationId: number): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(`${config.public.apiUrl}/sdg-predictions/publications/${publicationId}`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG predictions for publication ID ${publicationId}: ${error}`);
    }
  }

  // Fetch default model SDG predictions for a single publication ID
  async function getDefaultModelSDGPredictionsByPublicationId(publicationId: number): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(`${config.public.apiUrl}/sdg-predictions/publications/${publicationId}/default-model`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch default model SDG predictions for publication ID ${publicationId}: ${error}`);
    }
  }

  // Fetch distribution metrics for a list of publication IDs
  async function getDistributionMetricsByPublicationIds(publicationIds: number[]): Promise<any[]> {
    try {
      const response = await $fetch<any[]>(`${config.public.apiUrl}/sdg-predictions/publications/metrics`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
        body: {
          publications_ids: publicationIds,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch distribution metrics: ${error}`);
    }
  }

  // Fetch metrics for a single publication ID
  async function getPublicationMetricsById(publicationId: number): Promise<any> {
    try {
      const response = await $fetch<any>(`${config.public.apiUrl}/sdg-predictions/publications/${publicationId}/metrics`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch metrics for publication ID ${publicationId}: ${error}`);
    }
  }

  // Fetch top or bottom N publications based on a metric
  async function getPublicationsByMetric(metricType: string, order: string, topN: number): Promise<any[]> {
    try {
      const response = await $fetch<any[]>(`${config.public.apiUrl}/sdg-predictions/publications/metrics/${metricType}/${order}/${topN}`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch publications by metric: ${error}`);
    }
  }

  // Fetch SDG predictions for a specific part of dimensionality reductions
  async function getSDGPredictionsForDimensionalityReductionsPartitioned(
    reductionShorthand: string,
    partNumber: number,
    totalParts: number
  ): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(
        `${config.public.apiUrl}/sdg-predictions/dimensionality-reductions/${reductionShorthand}/${partNumber}/${totalParts}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch partitioned SDG predictions: ${error}`);
    }
  }

  // Fetch SDG predictions for a specific SDG and level
  async function getSDGPredictionsByLevel(
    sdg: number,
    reductionShorthand: string,
    level: number
  ): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(
        `${config.public.apiUrl}/sdg-predictions/dimensionality-reductions/sdgs/${sdg}/${reductionShorthand}/${level}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG predictions for SDG ${sdg}, level ${level}: ${error}`);
    }
  }

  // Fetch SDG predictions for a given SDG, reduction shorthand, and scenario type
  async function getSDGPredictionsForDimensionalityReductionsWithScenario(
    sdg: number,
    reductionShorthand: string,
    scenarioType: string
  ): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(
        `${config.public.apiUrl}/sdg-predictions/dimensionality-reductions/sdgs/${sdg}/${reductionShorthand}/scenarios/${scenarioType}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(
        `Failed to fetch SDG predictions for SDG ${sdg}, scenario ${scenarioType}: ${error}`
      );
    }
  }

  // Fetch SDG Predictions for the Least-Labeled SDG
  async function getLeastLabeledSDGPredictions(topK: number): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(
        `${config.public.apiUrl}/sdg-predictions/global/scenarios/least-labeled/${topK}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch least-labeled SDG predictions: ${error}`);
    }
  }

// Fetch SDG Predictions for the SDGs with the Highest Entropy
  async function getMaxEntropySDGPredictions(topK: number): Promise<SDGPredictionSchemaFull[]> {
    try {
      const response = await $fetch<SDGPredictionSchemaFull[]>(
        `${config.public.apiUrl}/sdg-predictions/global/scenarios/max-entropy/${topK}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch max-entropy SDG predictions: ${error}`);
    }
  }



  return {
    getSDGPredictionsByIds,
    getSDGPredictionsByPublicationIds,
    getSDGPredictionsByPublicationId,
    getDefaultModelSDGPredictionsByPublicationId,
    getDistributionMetricsByPublicationIds,
    getPublicationMetricsById,
    getPublicationsByMetric,
    getSDGPredictionsForDimensionalityReductionsPartitioned,
    getSDGPredictionsByLevel,
    getSDGPredictionsForDimensionalityReductionsWithScenario,
    getLeastLabeledSDGPredictions,
    getMaxEntropySDGPredictions,
  };
}
