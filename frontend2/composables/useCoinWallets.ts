import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "~/utils/snakeToCamel";
import type { SDGCoinWalletSchemaFull, SDGCoinWalletHistorySchemaFull } from "~/types/sdgCoinWallet";

export default function useCoinWallets() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch all SDG coin wallets
  async function getSDGCoinWallets(): Promise<SDGCoinWalletSchemaFull[]> {
    try {
      const response = await $fetch<SDGCoinWalletSchemaFull[]>(`${config.public.apiUrl}/wallets/users/wallets`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG coin wallets: ${error}`);
    }
  }

  // Fetch a single SDG coin wallet by user ID
  async function getSDGCoinWalletByUserId(userId: number): Promise<SDGCoinWalletSchemaFull> {
    try {
      const response = await $fetch<SDGCoinWalletSchemaFull>(
        `${config.public.apiUrl}/wallets/users/${userId}/wallet`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG coin wallet: ${error}`);
    }
  }

  // Fetch the personal SDG coin wallet for the current user
  async function getPersonalSDGCoinWallet(): Promise<SDGCoinWalletSchemaFull> {
    try {
      const response = await $fetch<SDGCoinWalletSchemaFull>(
        `${config.public.apiUrl}/wallets/personal`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch personal SDG coin wallet: ${error}`);
    }
  }

  // Fetch SDG coin wallet history for a specific user
  async function getSDGCoinWalletHistory(userId: number): Promise<SDGCoinWalletHistorySchemaFull[]> {
    try {
      const response = await $fetch<SDGCoinWalletHistorySchemaFull[]>(
        `${config.public.apiUrl}/wallets/users/${userId}/wallets/histories`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch SDG coin wallet history: ${error}`);
    }
  }

  // Add a wallet increment for a specific user
  async function addSDGCoinWalletIncrement(
    userId: number,
    incrementData: { increment: number; reason?: string }
  ): Promise<SDGCoinWalletHistorySchemaFull> {
    try {
      const response = await $fetch<SDGCoinWalletHistorySchemaFull>(
        `${config.public.apiUrl}/wallets/users/${userId}/wallets/histories`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
          body: incrementData,
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to add SDG coin wallet increment: ${error}`);
    }
  }

  return {
    getSDGCoinWallets,
    getSDGCoinWalletByUserId,
    getPersonalSDGCoinWallet,
    getSDGCoinWalletHistory,
    addSDGCoinWalletIncrement,
  };
}
