import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull } from "~/types/sdgLabelDecision";
import { snakeToCamel } from "~/utils/snakeToCamel";

export default function useSDGLabelDecisions() {
  const config = useRuntimeConfig();
  const accessToken = useCookie("access_token");


  async function getSDGLabelDecisionsByPublicationId(publicationId: number): Promise<SDGLabelDecisionSchemaFull[]> {
    try {
      const response = await $fetch<SDGLabelDecisionSchemaFull[]>(
        `${config.public.apiUrl}/label_decisions/publications/${publicationId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG user labels: ${error}`);
    }
  }

  return {
    getSDGLabelDecisionsByPublicationId,
  };
}
