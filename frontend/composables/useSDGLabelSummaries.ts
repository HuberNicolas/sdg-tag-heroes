import { useRuntimeConfig, useCookie } from "nuxt/app";
import type {
  SDGLabelSummarySchemaBase,
  SDGLabelSummarySchemaFull,
} from "~/types/sdgLabelSummaries";

export default function useSDGLabelSummaries() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch all SDG Label Summaries
  async function getSDGLabelSummaries(): Promise<SDGLabelSummarySchemaFull[]> {
    try {
      return await $fetch<SDGLabelSummarySchemaFull[]>(`${config.public.apiUrl}/label-summaries`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
    } catch (error) {
      throw new Error(`Failed to fetch SDG Label Summaries: ${error}`);
    }
  }

  // Fetch a single SDG Label Summary by ID
  async function getSDGLabelSummaryById(labelSummaryId: number): Promise<SDGLabelSummarySchemaFull> {
    try {
      return await $fetch<SDGLabelSummarySchemaFull>(
        `${config.public.apiUrl}/label-summaries/${labelSummaryId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
    } catch (error) {
      throw new Error(`Failed to fetch SDG Label Summary: ${error}`);
    }
  }

  // Fetch SDG Label Summary for a specific publication
  async function getSDGLabelSummaryByPublicationId(publicationId: number): Promise<SDGLabelSummarySchemaFull> {
    try {
      return await $fetch<SDGLabelSummarySchemaFull>(
        `${config.public.apiUrl}/label-summaries/publications/${publicationId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
    } catch (error) {
      throw new Error(`Failed to fetch SDG Label Summary for publication: ${error}`);
    }
  }

  return {
    getSDGLabelSummaries,
    getSDGLabelSummaryById,
    getSDGLabelSummaryByPublicationId,
  };
}
