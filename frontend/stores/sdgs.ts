import { defineStore } from 'pinia';
import { useRuntimeConfig } from 'nuxt/app';
import type { SDGGoal } from '@/types/schemas';

export const useSDGStore = defineStore('sdgs', {
  state: () => ({
    goals: [] as SDGGoal[], // Array to hold loaded SDG goals
    loading: false, // State to indicate loading status
    error: null as string | null, // State to hold any error messages
    selectedGoal: null,
  }),

  actions: {
    async fetchSDGGoals() {
      const config = useRuntimeConfig(); // Access runtime config
      const apiUrl = config.public.apiUrl; // Retrieve the hardcoded API URL
      this.loading = true;
      this.error = null;

      try {
        const response = await $fetch<SDGGoal[]>(`${apiUrl}sdgs`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        this.goals = response;
      } catch (error: any) {
        this.error = error.message || 'Failed to fetch SDG goals';
      } finally {
        this.loading = false;
      }
    },
  },
});
