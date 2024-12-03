import { defineStore } from 'pinia';
import { useRuntimeConfig } from 'nuxt/app';
import { DimensionalityReductionGroupedResponse } from '~/types/dimensionalityReduction';

export const useDimensionalityReductionsStore = defineStore('dimensionalityReductions', {
  state: () => ({
    reductions: {} as Record<
      number,
      {
        levels: Record<
          number,
          { reductions: DimensionalityReduction[]; stats: DimensionalityReductionStats | null }
        >;
      }
    >,
    fetching: false,
    error: null as Error | null,
  }),

  getters: {
    // Getter to access reductions for a specific SDG and level
    getReductionsForLevel: (state) => (sdgId: number, levelId: number) => {
      const sdgData = state.reductions[sdgId];
      if (!sdgData) return null;

      const levelData = sdgData.levels[levelId]; // Access level data
      if (!levelData) return null;

      return levelData.reductions || null; // Return reductions for the level
    },
  },

  actions: {
    async fetchReductions(sdgId: number) {
      // Check if data for this SDG is already in the store
      if (this.reductions[sdgId]) {
        return; // Already fetched
      }

      const config = useRuntimeConfig();
      this.fetching = true;
      this.error = null;

      try {
        const levels = [1, 2, 3]; // Define the levels to fetch
        this.reductions[sdgId] = { levels: {} }; // Initialize the SDG structure

        // Fetch data for all levels in parallel
        const fetchPromises = levels.map((level) =>
          $fetch<DimensionalityReductionGroupedResponse>(
            `${config.public.apiUrl}dimensionality_reductions?sdg=${sdgId}&level=${level}`,
            {
              method: 'GET',
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`,
              },
            }
          )
        );

        const results = await Promise.all(fetchPromises);

        // Process the results for each level
        results.forEach((result, index) => {
          const level = levels[index]; // Current level being processed

          // Initialize the level structure if not present
          if (!this.reductions[sdgId].levels[level]) {
            this.reductions[sdgId].levels[level] = { reductions: [], stats: null };
          }

          // Assign reductions and stats for the specific level
          const reductions = result.reductions[`sdg${sdgId}`]?.[`level${level}`] || [];
          const stats = result.stats.sdg_breakdown[`sdg${sdgId}`] || null;

          this.reductions[sdgId].levels[level] = { reductions, stats };
        });

        console.log(`Finished loading reductions for SDG ${sdgId}`);
      } catch (err) {
        this.error = err as Error;
      } finally {
        this.fetching = false;
      }
    },


    async fetchReductionsPerLevel(sdgId: number, level: number) {
      // Check if data for this SDG and level is already in the store
      if (this.reductions[sdgId]?.levels[level]?.reductions?.length) {
        return; // Already fetched
      }

      const config = useRuntimeConfig();
      this.fetching = true;
      this.error = null;

      try {
        const queryParams = new URLSearchParams({ sdg: sdgId.toString(), level: level.toString() });

        const result = await $fetch<DimensionalityReductionGroupedResponse>(
          `${config.public.apiUrl}dimensionality_reductions?${queryParams.toString()}`,
          {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
          }
        );

        // Initialize the SDG structure if not present
        if (!this.reductions[sdgId]) {
          this.reductions[sdgId] = { levels: {} };
        }

        // Initialize the level structure if not present
        if (!this.reductions[sdgId].levels[level]) {
          this.reductions[sdgId].levels[level] = { reductions: [], stats: null };
        }

        // Assign reductions and stats for the specific level
        const reductions = result.reductions[`sdg${sdgId}`]?.[`level${level}`] || [];
        const stats = result.stats.sdg_breakdown[`sdg${sdgId}`] || null;

        this.reductions[sdgId].levels[level] = { reductions, stats };

        console.log(`Finished loading reductions for SDG ${sdgId}, Level ${level}`);
      } catch (err) {
        this.error = err as Error;
      } finally {
        this.fetching = false;
      }
    },

  },
});
