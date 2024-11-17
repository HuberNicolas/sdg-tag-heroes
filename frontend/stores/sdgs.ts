import { defineStore } from 'pinia';
import type { SDGGoal } from '@/types/schemas'; // Import your SDGGoal type

// Define a Pinia store for managing SDG goals
export const useSDGStore = defineStore('sdgs', {
  state: () => ({
    sdgGoals: [] as SDGGoal[], // Array to hold loaded SDG goals
    loading: false, // State to indicate loading status
    error: null as string | null // State to hold any error messages
  }),

  actions: {
    // Action to load and store SDG goals
    async loadSDGGoals(fetchSDGGoalsFn: () => Promise<SDGGoal[]>) {
      this.loading = true;
      this.error = null;
      try {
        const goals = await fetchSDGGoalsFn();
        this.sdgGoals = goals;
      } catch (err: any) {
        this.error = err.message || 'Failed to load SDG goals';
        console.error('Error loading SDG goals:', err);
      } finally {
        this.loading = false;
      }
    },

    // Action to clear SDG goals from the store
    clearSDGGoals() {
      this.sdgGoals = [];
    }
  }
});
