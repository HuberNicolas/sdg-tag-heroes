import { snakeToCamel } from "../utils/snakeToCamel";
import { useCookie, useRuntimeConfig } from "nuxt/app";
import type {
  FactSchemaFull,
  PublicationIdsRequest,
  PublicationKeywordsSchema,
  PublicationSchemaBase,
  PublicationSchemaFull,
  PublicationsCollectiveSummarySchema,
  PublicationSDGAnalysisSchema,
  PublicationSimilaritySchema,
  PublicationSummarySchema
} from "~/types/publication";

export default function usePublications() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch publications by IDs
  async function getPublicationsByIds(
    publicationIds: number[]
  ): Promise<PublicationSchemaBase[]> {
    try {
      const response = await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications`,
        {
          method: "POST",
          body: { publication_ids: publicationIds } as PublicationIdsRequest,
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch publications: ${error}`);
    }
  }

  // Fetch all publications (paginated)
  async function getAllPublications(): Promise<PublicationSchemaBase[]> {
    try {
      const response = await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch publications: ${error}`);
    }
  }

  // Fetch a single publication by ID
  async function getPublicationById(
    publicationId: number
  ): Promise<PublicationSchemaFull> {
    try {
      const response = await $fetch<PublicationSchemaFull>(
        `${config.public.apiUrl}/publications/${publicationId}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch publication: ${error}`);
    }
  }

  // Fetch similar publications
  async function getSimilarPublications(
    topK: number,
    userQuery: string,
    publicationIds: number[]
  ): Promise<PublicationSimilaritySchema> {
    try {
      const response = await $fetch<PublicationSimilaritySchema>(
        `${config.public.apiUrl}/publications/similar/${topK}`,
        {
          method: "POST",
          body: { user_query: userQuery, publication_ids: publicationIds },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch similar publications: ${error}`);
    }
  }

  // Fetch SDG analysis for a publication
  async function getPublicationSDGAnalysis(
    publicationId: number,
    sdgId: number
  ): Promise<PublicationSDGAnalysisSchema> {
    try {
      const response = await $fetch<PublicationSDGAnalysisSchema>(
        `${config.public.apiUrl}/publications/${publicationId}/explain/goal/${sdgId}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG analysis: ${error}`);
    }
  }

  // Fetch keywords for a publication
  async function getPublicationKeywords(
    publicationId: number
  ): Promise<PublicationKeywordsSchema> {
    try {
      const response = await $fetch<PublicationKeywordsSchema>(
        `${config.public.apiUrl}/publications/${publicationId}/keywords`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch keywords: ${error}`);
    }
  }

  // Fetch a "Did You Know" fact for a publication
  async function getPublicationFact(
    publicationId: number
  ): Promise<FactSchemaFull> {
    try {
      const response = await $fetch<FactSchemaFull>(
        `${config.public.apiUrl}/publications/${publicationId}/facts`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch fact: ${error}`);
    }
  }

  // Fetch a summary for a publication
  async function getPublicationSummary(
    publicationId: number
  ): Promise<PublicationSummarySchema> {
    try {
      const response = await $fetch<PublicationSummarySchema>(
        `${config.public.apiUrl}/publications/${publicationId}/summary`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch summary: ${error}`);
    }
  }

  // Fetch a collective summary for multiple publications
  async function getCollectiveSummary(
    publicationIds: number[]
  ): Promise<PublicationsCollectiveSummarySchema> {
    try {
      const response = await $fetch<PublicationsCollectiveSummarySchema>(
        `${config.public.apiUrl}/publications/collective-summaries`,
        {
          method: "POST",
          body: { publication_ids: publicationIds },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch collective summary: ${error}`);
    }
  }

  // Fetch publications for a specific part of dimensionality reductions
  async function getPublicationsForDimensionalityReductionsPartitioned(
    reductionShorthand: string,
    partNumber: number,
    totalParts: number
  ): Promise<PublicationSchemaBase[]> {
    try {
      return await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/dimensionality-reductions/${reductionShorthand}/${partNumber}/${totalParts}/publications`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
    } catch (error) {
      throw new Error(`Failed to fetch publications for partitioned dimensionality reductions: ${error}`);
    }
  }


  return {
    getPublicationsByIds,
    getAllPublications,
    getPublicationById,
    getSimilarPublications,
    getPublicationSDGAnalysis,
    getPublicationKeywords,
    getPublicationFact,
    getPublicationSummary,
    getCollectiveSummary,
    getPublicationsForDimensionalityReductionsPartitioned,
  };
}
