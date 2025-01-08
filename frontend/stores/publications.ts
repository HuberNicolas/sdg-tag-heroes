import { defineStore } from 'pinia';
import { useRuntimeConfig } from 'nuxt/app';
import type { PublicationSchemaFull } from '~/types/publicationSchema';
const config = useRuntimeConfig();

export const usePublicationsStore = defineStore('publications', {
  state: () => ({
    publications: {} as Record<number, Record<number, Record<number, PublicationSchemaFull>>>, // SDG -> Level -> Publication ID -> Publication
    selectedPublication: null,
    fetching: false,
    loading: false,
    error: null as Error | null,
  }),
  getters: {
    // General getter to retrieve publications dynamically
    getPublications: (state) => {
      return (sdgId?: number, levelId?: number, publicationId?: number) => {

        // If sdgId is not provided, return the entire publications object
        if (sdgId === undefined) return state.publications;

        // If levelId is not provided, return all levels for the specified SDG
        const sdgLevels = state.publications[sdgId];
        if (levelId === undefined) return sdgLevels || {};

        // If publicationId is not provided, return all publications for the specified level
        const levelPublications = sdgLevels?.[levelId];
        if (publicationId === undefined) return levelPublications || {};

        // Return the specific publication, or null if not found
        return levelPublications?.[publicationId] || null;
      };
    },
    getSelectedPublication: (state) => {
      return state.selectedPublications;
    }
  },
  actions: {
    // Fetch a single publication by ID
    async fetchPublication(publicationId: number) {
      if (this.selectedPublication && this.selectedPublication.publication_id === publicationId) {
        return; // Already fetched and selected
      }

      this.fetching = true;
      this.error = null;

      try {
        const response = await $fetch<PublicationSchemaFull>(`${config.public.apiUrl}publications/${publicationId}`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        this.selectedPublication = response;
      } catch (err) {
        this.error = err as Error;
      } finally {
        this.fetching = false;
      }
    },


    // Fetch multiple publications by IDs for a specific SDG and level
    async fetchPublicationsBatch(sdgId: number, levelId: number, publicationIds: number[]) {
      const config = useRuntimeConfig();
      console.log("Called fetchPublicationsBatch ")
      const missingIds = publicationIds.filter(
        (id) => !this.publications[sdgId]?.[levelId]?.[id]
      );

      if (missingIds.length === 0) {
        return; // All publications already fetched
      }

      this.fetching = true;
      this.error = null;

      try {
        const response = await $fetch<PublicationSchemaFull[]>(`${config.public.apiUrl}publications/`, {
          method: 'POST',
          body:  { publication_ids: missingIds },
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        if (!this.publications[sdgId]) {
          this.publications[sdgId] = {};
        }
        if (!this.publications[sdgId][levelId]) {
          this.publications[sdgId][levelId] = {};
        }

        // If response.data contains the array, use that
        const publicationsArray = Array.isArray(response) ? response : response.data;

        publicationsArray.forEach((pub) => {
          this.publications[sdgId][levelId][pub.publication_id] = pub;
        });
      } catch (err) {
        this.error = err as Error;
      } finally {
        this.fetching = false;
      }
    },
  },
});
