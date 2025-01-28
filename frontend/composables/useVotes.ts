import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { VoteSchemaBase, VoteSchemaFull } from "~/types/vote";
import { snakeToCamel } from "~/utils/snakeToCamel";

export default function useVotes() {
  const config = useRuntimeConfig();
  const accessToken = useCookie("access_token");

  async function getVotes(): Promise<VoteSchemaFull[]> {
    try {
      const response = await $fetch<VoteSchemaFull[]>(
        `${config.public.apiUrl}/votes`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch votes: ${error}`);
    }
  }

  async function getVoteById(voteId: number): Promise<VoteSchemaFull> {
    try {
      const response = await $fetch<VoteSchemaFull>(
        `${config.public.apiUrl}/votes/${voteId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch vote: ${error}`);
    }
  }

  return {
    getVotes,
    getVoteById,
  };
}
