import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "~/utils/snakeToCamel";
import type { SDGCoinWalletHistorySchemaFull } from "~/types/sdgCoinWalletHistory";

export default function useCoinWalletHistories() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch latest SDG Coin wallet history
  async function getLatestSDGCoinWalletHistory(): Promise<SDGCoinWalletHistorySchemaFull | null> {
    try {
      const response = await $fetch<SDGCoinWalletHistorySchemaFull>(`${config.public.apiUrl}/wallets/latest`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return response ? snakeToCamel(response) : null;
    } catch (error) {
      throw new Error(`Failed to fetch latest SDG Coin wallet history: ${error}`);
    }
  }

  return {
    getLatestSDGCoinWalletHistory,
  };
}
