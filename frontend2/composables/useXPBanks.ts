import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "~/utils/snakeToCamel";
import type { SDGXPBankSchemaFull, SDGXPBankHistorySchemaFull } from "~/types/sdgXpBank";

export default function useXPBanks() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch all XP banks
  async function getXPBanks(): Promise<SDGXPBankSchemaFull[]> {
    try {
      const response = await $fetch<SDGXPBankSchemaFull[]>(`${config.public.apiUrl}/banks/users/banks`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch XP banks: ${error}`);
    }
  }

  // Fetch a single XP bank by user ID
  async function getXPBankByUserId(userId: number): Promise<SDGXPBankSchemaFull> {
    try {
      const response = await $fetch<SDGXPBankSchemaFull>(
        `${config.public.apiUrl}/banks/users/${userId}/bank`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch XP bank: ${error}`);
    }
  }

  // Fetch the personal XP bank for the current user
  async function getPersonalXPBank(): Promise<SDGXPBankSchemaFull> {
    try {
      const response = await $fetch<SDGXPBankSchemaFull>(
        `${config.public.apiUrl}/banks/personal`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch personal XP bank: ${error}`);
    }
  }

  // Fetch XP bank history for a specific user
  async function getXPBankHistory(userId: number): Promise<SDGXPBankHistorySchemaFull[]> {
    try {
      const response = await $fetch<SDGXPBankHistorySchemaFull[]>(
        `${config.public.apiUrl}/users/${userId}/banks/histories`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch XP bank history: ${error}`);
    }
  }

  // Add an XP bank increment for a specific user
  async function addXPBankIncrement(
    userId: number,
    incrementData: { sdg: string; increment: number; reason?: string }
  ): Promise<SDGXPBankHistorySchemaFull> {
    try {
      const response = await $fetch<SDGXPBankHistorySchemaFull>(
        `${config.public.apiUrl}/users/${userId}/banks/histories`,
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
      throw new Error(`Failed to add XP bank increment: ${error}`);
    }
  }

  return {
    getXPBanks,
    getXPBankByUserId,
    getPersonalXPBank,
    getXPBankHistory,
    addXPBankIncrement,
  };
}
