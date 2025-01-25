import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { SDGGoalSchemaFull } from "~/types/sdgs";
import { snakeToCamel } from "../utils/snakeToCamel";

export default function useSDGs() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch all SDG goals
  async function getSDGs(): Promise<SDGGoalSchemaFull[]> {
    try {
      const response = await $fetch<SDGGoalSchemaFull[]>(`${config.public.apiUrl}/sdgs`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDGs: ${error}`);
    }
  }

  // Fetch a single SDG goal by ID
  async function getSDGById(sdgId: number): Promise<SDGGoalSchemaFull> {
    try {
      const response = await $fetch<SDGGoalSchemaFull>(
        `${config.public.apiUrl}/sdgs/${sdgId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG: ${error}`);
    }
  }

  return {
    getSDGs,
    getSDGById,
  };
}
