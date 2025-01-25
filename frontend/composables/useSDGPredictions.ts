import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "~/utils/snakeToCamel";
import type { SDGPredictionSchemaFull } from "~/types/sdgPredictions";

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
      return response;
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
      return response;
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
      return response;
    } catch (error) {
      throw new Error(`Failed to fetch publications by metric: ${error}`);
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
  };
}
