import { useCookie, useRuntimeConfig } from "nuxt/app";
import type {
  SDGLabelDecisionSchemaBase,
  SDGLabelDecisionSchemaExtended,
  SDGLabelDecisionSchemaFull
} from "~/types/sdgLabelDecision";
import { snakeToCamel } from "~/utils/snakeToCamel";
import type { SDGUserLabelsCommentSummarySchema } from "~/types/sdgUserLabel";

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
  ): Promise<SDGLabelDecisionSchemaExtended[]> {
    try {
      const response = await $fetch<SDGLabelDecisionSchemaExtended[]>(
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

  async function getScenarioSDGLabelDecisionsForReduction(
    sdg: number,
    reductionShorthand: string,
    scenarioType: string
  ): Promise<SDGLabelDecisionSchemaFull[]> {
    try {
      const response = await $fetch<SDGLabelDecisionSchemaFull[]>(
        `${config.public.apiUrl}/label-decisions/sdgs/${sdg}/${reductionShorthand}/scenarios/${scenarioType}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch scenario SDG Label Decisions: ${error}`);
    }
  }

  // Retrieve all SDGLabelDecisions that a user has interacted with.
  async function getSDGLabelDecisionsForUser(
    userId: number,
  ): Promise<SDGLabelDecisionSchemaExtended[]> {
    try {
      const response = await $fetch<SDGLabelDecisionSchemaExtended[]>(
        `${config.public.apiUrl}/label-decisions/users/${userId}/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG label decisions: ${error}`);
    }
  }


  return {
    getSDGLabelDecisionsByPublicationId,
    createCommentSummary,
    getSDGLabelDecisionsForReduction,
    getScenarioSDGLabelDecisionsForReduction,
    getSDGLabelDecisionsForUser,
  };
}
