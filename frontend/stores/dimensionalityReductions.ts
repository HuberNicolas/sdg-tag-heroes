import { defineStore } from 'pinia';
import { useRuntimeConfig } from 'nuxt/app';
import { DimensionalityReductionResponse } from '~/types/dimensionalityReduction';

export const useDimensionalityReductionsStore = defineStore('dimensionalityReductions', {
  state: () => ({
    reductions: {} as Record<number, DimensionalityReductionResponse | null>,
    fetching: false,
    error: null as Error | null,
  }),
  actions: {
    async fetchReductions(sdgId: number) {
      if (this.reductions[sdgId]) {
        return; // Already fetched
      }

      const config = useRuntimeConfig();
      this.fetching = true;
      this.error = null;

      try {
        const levels = [1, 2, 3];
        const fetchPromises = levels.map((level) =>
          $fetch<DimensionalityReductionResponse>(
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

        // Merge all levels into one response
        const reductions: DimensionalityReductionResponse = {
          reductions: {},
          stats: {
            total_sdg_groups: 0,
            total_levels: 0,
            total_reductions: 0,
            sdg_breakdown: {},
          },
        };

        results.forEach((result) => {
          Object.entries(result.reductions).forEach(([sdg, levels]) => {
            if (!reductions.reductions[sdg]) {
              reductions.reductions[sdg] = {};
            }
            Object.entries(levels).forEach(([level, data]) => {
              reductions.reductions[sdg][level] = data;
            });
          });
          reductions.stats.total_sdg_groups += result.stats.total_sdg_groups;
          reductions.stats.total_levels += result.stats.total_levels;
          reductions.stats.total_reductions += result.stats.total_reductions;
          Object.entries(result.stats.sdg_breakdown).forEach(([sdg, stats]) => {
            if (!reductions.stats.sdg_breakdown[sdg]) {
              reductions.stats.sdg_breakdown[sdg] = { total_levels: 0, total_reductions: 0 };
            }
            reductions.stats.sdg_breakdown[sdg].total_levels += stats.total_levels;
            reductions.stats.sdg_breakdown[sdg].total_reductions += stats.total_reductions;
          });
        });

        this.reductions[sdgId] = reductions;
      } catch (err) {
        this.error = err as Error;
      } finally {
        this.fetching = false;
      }
    },
  },
});
