import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "../utils/snakeToCamel";
import type {
  DimensionalityReductionPublicationIdsRequest,
  DimensionalityReductionSchemaFull,
  FilteredDimensionalityReductionStatisticsSchema,
  GroupedDimensionalityReductionResponseSchema,
  UserCoordinatesRequest,
  UserCoordinatesSchema
} from "~/types/dimensionalityReduction";

export default function useDimensionalityReductions() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch all dimensionality reductions
  async function getDimensionalityReductions(): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      const response = await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch dimensionality reductions: ${error}`);
    }
  }

  // Fetch dimensionality reductions for specific publications
  async function getDimensionalityReductionsForPublications(
    request: DimensionalityReductionPublicationIdsRequest,
    reductionShorthand: string = "UMAP-15-0.1-2"
  ): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      const response = await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/publications/${reductionShorthand}`,
        {
          method: "POST",
          body: request,
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch dimensionality reductions for publications: ${error}`);
    }
  }

  // Fetch dimensionality reductions for a specific publication
  async function getDimensionalityReductionsForPublication(
    publicationId: number,
    reductionShorthand: string = "UMAP-15-0.1-2"
  ): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      const response = await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/publications/${publicationId}/${reductionShorthand}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch dimensionality reductions for publication: ${error}`);
    }
  }

  // Fetch filtered dimensionality reductions by SDG range
  async function getFilteredDimensionalityReductions(
    sdgRange: [number, number],
    limit: number = 10,
    sdgs?: number[],
    model?: string,
    level?: number[],
    reductionShorthand?: string
  ): Promise<FilteredDimensionalityReductionStatisticsSchema> {
    try {
      const response = await $fetch<FilteredDimensionalityReductionStatisticsSchema>(
        `${config.public.apiUrl}/dimensionality-reductions/filtered`,
        {
          query: {
            sdg_range: sdgRange,
            limit,
            sdgs,
            model,
            level,
            reduction_shorthand: reductionShorthand,
          },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch filtered dimensionality reductions: ${error}`);
    }
  }

  // Fetch grouped dimensionality reductions by SDG and level
  async function getGroupedDimensionalityReductions(
    sdg: number[],
    level: number[],
    reductionShorthand?: string,
    limit: number = 200
  ): Promise<GroupedDimensionalityReductionResponseSchema> {
    try {
      const response = await $fetch<GroupedDimensionalityReductionResponseSchema>(
        `${config.public.apiUrl}/dimensionality-reductions/grouped`,
        {
          query: {
            sdg,
            level,
            reduction_shorthand: reductionShorthand,
            limit,
          },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch grouped dimensionality reductions: ${error}`);
    }
  }

  // Calculate user coordinates for dimensionality reduction
  async function calculateUserCoordinates(
    request: UserCoordinatesRequest
  ): Promise<UserCoordinatesSchema> {
    try {
      const response = await $fetch<UserCoordinatesSchema>(
        `${config.public.apiUrl}/dimensionality-reductions/user-coordinates`,
        {
          method: "POST",
          body: request,
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to calculate user coordinates: ${error}`);
    }
  }


  // Fetch a specific part of dimensionality reductions
  async function getDimensionalityReductionsPartitioned(
    reductionShorthand: string,
    partNumber: number,
    totalParts: number
  ): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      const response = await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/${reductionShorthand}/${partNumber}/${totalParts}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch partitioned dimensionality reductions: ${error}`);
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
        `${config.public.apiUrl}/dimensionality-reductions/sdgs/${sdg}/${reductionShorthand}/${level}/`,
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

  // Fetch dimensionality reductions by SDG and scenario type
  async function getDimensionalityReductionsBySDGAndScenario(
    sdg: number,
    reductionShorthand: string,
    scenarioType: string
  ): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      const response = await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/sdgs/${sdg}/${reductionShorthand}/scenarios/${scenarioType}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch dimensionality reductions for SDG ${sdg}, scenario ${scenarioType}: ${error}`);
    }
  }

  // Fetch Dimensionality Reductions for the Least-Labeled SDG
  async function getLeastLabeledDimensionalityReductions(topK: number): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      const response = await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/global/scenarios/least-labeled/${topK}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch least-labeled dimensionality reductions: ${error}`);
    }
  }

// Fetch Dimensionality Reductions for the SDGs with the Highest Entropy
  async function getMaxEntropyDimensionalityReductions(topK: number): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      const response = await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/global/scenarios/max-entropy/${topK}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch max-entropy dimensionality reductions: ${error}`);
    }
  }





  return {
    getDimensionalityReductions,
    getDimensionalityReductionsForPublications,
    getDimensionalityReductionsForPublication,
    getFilteredDimensionalityReductions,
    getGroupedDimensionalityReductions,
    calculateUserCoordinates,
    getDimensionalityReductionsPartitioned,
    getSDGPredictionsByLevel,
    getDimensionalityReductionsBySDGAndScenario,
    getLeastLabeledDimensionalityReductions,
    getMaxEntropyDimensionalityReductions,
  };
}
