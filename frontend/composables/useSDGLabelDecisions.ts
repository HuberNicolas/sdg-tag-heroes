import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull } from "~/types/sdgLabelDecision";
import { snakeToCamel } from "~/utils/snakeToCamel";

export default function useSDGLabelDecisions() {
  const config = useRuntimeConfig();
  const accessToken = useCookie("access_token");


  async function getSDGLabelDecisionsByPublicationId(publicationId: number): Promise<SDGLabelDecisionSchemaFull[]> {
    try {
      const response = await $fetch<SDGLabelDecisionSchemaFull[]>(
        `${config.public.apiUrl}/label-decisions/publications/${publicationId}`,
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

  async function createCommentSummary(userLabelIds: number[]): Promise<SDGUserLabelsCommentSummarySchema> {
    try {
      const response = await $fetch<SDGUserLabelsCommentSummarySchema>(
        `${config.public.apiUrl}/user-labels/summary`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
          body: {
            user_labels_ids: userLabelIds,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch comment summary: ${error}`);
    }
  }

  async function getSDGLabelDecisionsForReduction(
    sdg: number,
    reductionShorthand: string,
    level: number
  ): Promise<SDGLabelDecisionSchemaFull[]> {
    try {
      const response = await $fetch<SDGLabelDecisionSchemaFull[]>(
        `${config.public.apiUrl}/label-decisions/dimensionality-reductions/sdgs/${sdg}/${reductionShorthand}/${level}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch newest SDG Label Decisions: ${error}`);
    }
  }

  return {
    getSDGLabelDecisionsByPublicationId,
    createCommentSummary,
    getSDGLabelDecisionsForReduction,
  };
}
