import { defineStore } from "pinia";
import { useRuntimeConfig } from "nuxt/app";

export const useUserStore = defineStore("sdg", {
  state: () => ({
    sdgCoins: {} as Record<number, number>, // Cache: userId -> totalCoins
    sdgXP: {} as Record<number, number>, // Cache: userId -> totalXP
    fetching: false,
    error: null as Error | null,
  }),
  actions: {
    // Fetch SDG Coins for a user
    async fetchSDGCoins(userId: number): Promise<number> {
      // Return cached value if it exists
      if (this.sdgCoins[userId] !== undefined) {
        return this.sdgCoins[userId];
      }

      this.fetching = true;
      this.error = null;

      try {
        const config = useRuntimeConfig();
        const token = localStorage.getItem("access_token");
        if (!token) {
          throw new Error("No access token found");
        }

        const url = `${config.public.apiUrl}users/${userId}/wallet`;
        const response = await $fetch<{ total_coins: number }>(url, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        // Cache and return total coins
        this.sdgCoins[userId] = response.total_coins;
        return response.total_coins;
      } catch (error) {
        console.error("Failed to fetch SDG Coins", error);
        this.error = error as Error;
        throw new Error("Failed to fetch SDG Coins");
      } finally {
        this.fetching = false;
      }
    },

    // Fetch SDG XP for a user
    async fetchSDGXP(userId: number): Promise<number> {
      // Return cached value if it exists
      if (this.sdgXP[userId] !== undefined) {
        return this.sdgXP[userId];
      }

      this.fetching = true;
      this.error = null;

      try {
        const config = useRuntimeConfig();
        const token = localStorage.getItem("access_token");
        if (!token) {
          throw new Error("No access token found");
        }

        const url = `${config.public.apiUrl}users/${userId}/bank`;
        const response = await $fetch<{ total_xp: number }>(url, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        // Cache and return total XP
        this.sdgXP[userId] = response.total_xp;
        return response.total_xp;
      } catch (error) {
        console.error("Failed to fetch SDG XP", error);
        this.error = error as Error;
        throw new Error("Failed to fetch SDG XP");
      } finally {
        this.fetching = false;
      }
    },
  },
});
