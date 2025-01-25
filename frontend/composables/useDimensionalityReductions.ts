import { useCookie, useRuntimeConfig } from "nuxt/app";
import type {
  DimensionalityReductionSchemaFull,
  PublicationSchemaBase,
  UserCoordinatesRequest,
  DimensionalityReductionPublicationIdsRequest,
  FilteredDimensionalityReductionStatisticsSchema,
  GroupedDimensionalityReductionResponseSchema,
  UserCoordinatesSchema,
} from "~/types/dimensionalityReduction";

export default function useDimensionalityReductions() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch all dimensionality reductions
  async function getDimensionalityReductions(): Promise<DimensionalityReductionSchemaFull[]> {
    try {
      return await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
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
      return await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/publications/${reductionShorthand}`,
        {
          method: "POST",
          body: request,
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
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
      return await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/publications/${publicationId}/${reductionShorthand}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
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
      return await $fetch<FilteredDimensionalityReductionStatisticsSchema>(
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
      return await $fetch<GroupedDimensionalityReductionResponseSchema>(
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
    } catch (error) {
      throw new Error(`Failed to fetch grouped dimensionality reductions: ${error}`);
    }
  }

  // Calculate user coordinates for dimensionality reduction
  async function calculateUserCoordinates(
    request: UserCoordinatesRequest
  ): Promise<UserCoordinatesSchema> {
    try {
      return await $fetch<UserCoordinatesSchema>(
        `${config.public.apiUrl}/dimensionality-reductions/user-coordinates`,
        {
          method: "POST",
          body: request,
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
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
      return await $fetch<DimensionalityReductionSchemaFull[]>(
        `${config.public.apiUrl}/dimensionality-reductions/${reductionShorthand}/${partNumber}/${totalParts}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
    } catch (error) {
      throw new Error(`Failed to fetch partitioned dimensionality reductions: ${error}`);
    }
  }

  return {
    getDimensionalityReductions,
    getDimensionalityReductionsForPublications,
    getDimensionalityReductionsForPublication,
    getFilteredDimensionalityReductions,
    getGroupedDimensionalityReductions,
    getDimensionalityReductionsPartitioned,
    calculateUserCoordinates,
  };
}
