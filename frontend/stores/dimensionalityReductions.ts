import { defineStore } from 'pinia';
import { useRuntimeConfig } from 'nuxt/app';
import { DimensionalityReductionGroupedResponse } from '~/types/dimensionalityReduction';
import { CollectiveSummaryResponse } from "~/types/collectiveSummary"; // Define your response typ


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
    selectedPoints: [],
    currentLevel: 1 as number,
    fetching: false,
    error: null as Error | null,
    selectedSummary: null as CollectiveSummaryResponse | null, // Add this field
  }),

  getters: {
    getCurrentLevel: state => state.currentLevel,
    // Getter to access reductions for a specific SDG and level
    getReductionsForLevel: (state) => (sdgId: number, levelId: number) => {
      const sdgData = state.reductions[sdgId];
      if (!sdgData) return null;

      const levelData = sdgData.levels[levelId]; // Access level data
      if (!levelData) return null;

      return levelData.reductions || null; // Return reductions for the level
    },
    getSelectedPublicationsIds: (state) => ()  => {
      return state.selectedPoints.forEach(point => {
        point.publication_id
      })
    }
  },

  actions: {
    setCurrentLevel(level: number) {
      this.currentLevel = level;
    },
    clearSelectedPoints() {
      this.selectedPoints = null;
    },
    clearSelectedSummary() {
      this.selectedSummary = null;
    },
    setSelectedPoints (points: any) {
      this.selectedPoints = points;
    },
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

    async computeSummaryForSelectedPoints() {
      if (this.selectedPoints.length === 0) {
        this.selectedSummary = null;
        return;
      }

      this.fetching = true; // Start loading
      const apiUrl = useRuntimeConfig().public.apiUrl;

      const data = {
        publication_ids: this.selectedPoints.map(point => point.publication_id),
      };

      try {
        const response = await $fetch<CollectiveSummaryResponse>(`${apiUrl}publications/summaries`, {
          method: "POST",
          body: data,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        this.selectedSummary = response;
      } catch (error) {
        console.error("Error computing summary:", error);
        this.selectedSummary = null;
        this.selectedSummary = null;
      } finally {
        this.fetching = false; // Stop loading
      }
    },

  },
});
