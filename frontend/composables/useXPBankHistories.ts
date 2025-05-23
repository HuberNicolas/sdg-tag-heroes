import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "~/utils/snakeToCamel";
import type { SDGXPBankHistorySchemaFull } from "~/types/sdgXpBankHistory";

export default function useXPBankHistories() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch latest XP bank history
  async function getLatestXPBankHistory(): Promise<SDGXPBankHistorySchemaFull | null> {
    try {
      const response = await $fetch<SDGXPBankHistorySchemaFull>(`${config.public.apiUrl}/banks/latest`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return response ? snakeToCamel(response) : null;
    } catch (error) {
      throw new Error(`Failed to fetch latest XP bank history: ${error}`);
    }
  }

  return {
    getLatestXPBankHistory,
  };
}
