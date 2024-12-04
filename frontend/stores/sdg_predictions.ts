import { defineStore } from 'pinia';
import { useRuntimeConfig } from 'nuxt/app';
import type { SDGPredictionSchemaFull } from '~/types/sdgPredictionSchema';

export const usePredictionsStore = defineStore('predictions', {
  state: () => ({
    predictions: {} as Record<number, Record<number, SDGPredictionSchemaFull>>, // SDG -> Prediction ID -> Prediction
    selectedPublicationPrediction: null,
    fetching: false,
    error: null as Error | null,
  }),
  getters: {
    // Getter to retrieve predictions dynamically

    getPredictionsForLevel: (state) => (sdgId: number, levelId: number) => {
      console.log(sdgId, levelId);
      const sdgData = state.predictions[sdgId];
      if (!sdgData) return null;
      console.log(sdgData)

      const levelData = sdgData[levelId]; // Access level data
      console.log(levelData)
      if (!levelData) return null;
      return levelData || null; // Return reductions for the level
    }


  },
  actions: {
    // Fetch multiple predictions by IDs for a specific SDG
    async fetchPredictionsBatch(sdgId: number, levelId:number, publicationsIds: number[]) {
      const config = useRuntimeConfig();

      this.fetching = true;
      this.error = null;

      try {
        // Fetch predictions using POST
        const response = await $fetch<SDGPredictionSchemaFull[]>(
          `${config.public.apiUrl}sdg_predictions/publications/`,
          {
            method: 'POST',
            body: { publications_ids: publicationsIds },
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
          }
        );

        // Ensure SDG storage exists
        if (!this.predictions[sdgId]) {
          this.predictions[sdgId] = {};
        }

        // Ensure level storage exists
        if (!this.predictions[sdgId][levelId]) {
          this.predictions[sdgId][levelId] = {};
        }

        // Store fetched predictions
        response.forEach((prediction) => {
          this.predictions[sdgId][levelId][prediction.prediction_id] = prediction;
        });
      } catch (err) {
        this.error = err as Error;
      } finally {
        this.fetching = false;
      }
    },
    async fetchPredictionsByPublicationId(publicationId: number) {
      console.log(publicationId);
      const config = useRuntimeConfig();

      this.fetching = true;
      this.error = null;

      try {
        // Fetch predictions using POST
        const response = await $fetch<SDGPredictionSchemaFull[]>(
          `${config.public.apiUrl}sdg_predictions/publications/${publicationId}`,
          {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
          }
        );

        // Replace existing predictions with the fetched ones
        this.selectedPublicationPrediction = response[0];

      } catch (err) {
        this.error = err as Error;
      } finally {
        this.fetching = false;
      }
    },
  },
});
