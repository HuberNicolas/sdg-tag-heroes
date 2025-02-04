import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { SDGUserLabelSchemaBase, SDGUserLabelSchemaFull, UserLabelRequest } from "~/types/sdgUserLabel";
import { snakeToCamel } from "~/utils/snakeToCamel";

export default function useUserLabels() {
  const config = useRuntimeConfig();
  const accessToken = useCookie("access_token");

  async function getSDGUserLabels(): Promise<SDGUserLabelSchemaFull[]> {
    try {
      const response = await $fetch<SDGUserLabelSchemaFull[]>(
        `${config.public.apiUrl}/user-labels`,
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

  async function getSDGUserLabelById(labelId: number): Promise<SDGUserLabelSchemaFull> {
    try {
      const response = await $fetch<SDGUserLabelSchemaFull>(
        `${config.public.apiUrl}/user-labels/${labelId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG user label: ${error}`);
    }
  }

  async function getSDGUserLabelsByPublicationId(publicationId: number): Promise<SDGUserLabelSchemaFull> {
    try {
      const response = await $fetch<SDGUserLabelSchemaFull>(
        `${config.public.apiUrl}/user-labels/publications/${publicationId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG user label: ${error}`);
    }
  }

  async function createOrLinkSDGUserLabel(
    request: UserLabelRequest
  ): Promise<SDGUserLabelSchemaFull> {
    try {
      const response = await $fetch<SDGUserLabelSchemaFull>(
        `${config.public.apiUrl}/user-labels`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
            "Content-Type": "application/json",
          },
          body: request,
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to create or link SDG user label: ${error}`);
    }
  }



  return {
    getSDGUserLabels,
    getSDGUserLabelById,
    getSDGUserLabelsByPublicationId,
    createOrLinkSDGUserLabel
  };
}
