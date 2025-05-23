import { snakeToCamel } from "~/utils/snakeToCamel";
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

import type {
  SummarySchemaBase,
  SummarySchemaFull
} from "~/types/summary";

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
    publicationIds: number[] = null
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
  ): Promise<SummarySchemaFull> {
    try {
      const response = await $fetch<SummarySchemaFull>(
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
      const response =  await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications/dimensionality-reductions/${reductionShorthand}/${partNumber}/${totalParts}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch publications for partitioned dimensionality reductions: ${error}`);
    }
  }

  // Fetch publications for a specific SDG, reduction shorthand, and level
  async function getPublicationsForDimensionalityReductions(
    sdg: number,
    reductionShorthand: string,
    level: number
  ): Promise<PublicationSchemaBase[]> {
    try {
      const response = await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications/dimensionality-reductions/sdgs/${sdg}/${reductionShorthand}/${level}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch publications for SDG ${sdg}, level ${level}: ${error}`);
    }
  }

  // Fetch publications for a given SDG, reduction shorthand, and scenario type
  async function getPublicationsForDimensionalityReductionsWithScenario(
    sdg: number,
    reductionShorthand: string,
    scenarioType: string
  ): Promise<PublicationSchemaBase[]> {
    try {
      const response = await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications/dimensionality-reductions/sdgs/${sdg}/${reductionShorthand}/scenarios/${scenarioType}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(
        `Failed to fetch publications for SDG ${sdg}, scenario ${scenarioType}: ${error}`
      );
    }
  }

  // Fetch publications by scenario type
  async function getPublicationsByScenario(
    scenarioType: string,
    topK: number,
  ): Promise<PublicationSchemaBase[]> {
    try {
      const response = await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications/scenarios/${scenarioType}/${topK}/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch publications for scenario type ${scenarioType}: ${error}`);
    }
  }

  // Fetch Publications for the Least-Labeled SDG
  async function getLeastLabeledPublications(topK: number): Promise<PublicationSchemaBase[]> {
    try {
      const response = await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications/global/scenarios/least-labeled/${topK}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch least-labeled publications: ${error}`);
    }
  }

// Fetch Publications for the SDGs with the Highest Entropy
  async function getMaxEntropyPublications(topK: number): Promise<PublicationSchemaBase[]> {
    try {
      const response = await $fetch<PublicationSchemaBase[]>(
        `${config.public.apiUrl}/publications/global/scenarios/max-entropy/${topK}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch max-entropy publications: ${error}`);
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
    getPublicationsForDimensionalityReductions,
    getPublicationsForDimensionalityReductionsWithScenario,
    getPublicationsByScenario,
    getLeastLabeledPublications,
    getMaxEntropyPublications,
  };
}
