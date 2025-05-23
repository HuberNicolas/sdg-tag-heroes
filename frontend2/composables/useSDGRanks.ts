import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { SDGRankSchemaFull, UserSDGRankSchemaFull } from "~/types/sdgRanks";
import { snakeToCamel } from "~/utils/snakeToCamel";

export default function useSDGRanks() {
  const config = useRuntimeConfig();
  const accessToken = useCookie("access_token");

  // Fetch all SDG ranks
  async function getSDGRanks(): Promise<SDGRankSchemaFull[]> {
    try {
      const response = await $fetch<SDGRankSchemaFull[]>(`${config.public.apiUrl}/ranks`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG ranks: ${error}`);
    }
  }

  // Fetch all SDG ranks for all Users
  async function getSDGRanksForUsers(): Promise<UserSDGRankSchemaFull[]> {
    try {
      const response = await $fetch<UserSDGRankSchemaFull[]>(`${config.public.apiUrl}/ranks/users`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG ranks: ${error}`);
    }
  }

  // Fetch a single SDG rank by ID
  async function getSDGRankByUserId(userId: number): Promise<SDGRankSchemaFull> {
    try {
      const response = await $fetch<SDGRankSchemaFull>(
        `${config.public.apiUrl}/ranks/users/${userId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG rank: ${error}`);
    }
  }

  return {
    getSDGRanks,
    getSDGRanksForUsers,
    getSDGRankByUserId,
  };
}
