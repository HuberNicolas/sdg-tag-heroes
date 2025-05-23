import { snakeToCamel } from "~/utils/snakeToCamel";
import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { ExplanationSchema } from "~/types/explanation";

export default function useExplanations() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch SHAP explanation by publication ID
  async function getExplanationByPublicationId(
    publicationId: number
  ): Promise<ExplanationSchema> {
    try {
      const response = await $fetch<ExplanationSchema>(
        `${config.public.apiUrl}/explanations/publications/${publicationId}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch explanation: ${error}`);
    }
  }

  return {
    getExplanationByPublicationId,
  };
}
