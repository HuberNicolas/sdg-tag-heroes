import { defineStore } from 'pinia';
import { useRuntimeConfig } from 'nuxt/app';
import type { PublicationSchemaFull } from '~/types/publicationSchema';
const config = useRuntimeConfig();

export const usePublicationsStore = defineStore('publications', {
  state: () => ({
    publications: {} as Record<number, Record<number, Record<number, PublicationSchemaFull>>>, // SDG -> Level -> Publication ID -> Publication
    selectedPublication: null,
    selectedPublications: [],
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
    },
    getSelectedPublications: (state) => {
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

    async fetchPublicationScores(publicationIds: number[]) {
      const config = useRuntimeConfig();
      const apiUrl = config.public.apiUrl;

      if (!publicationIds || publicationIds.length === 0) {
        console.warn("No publication IDs provided for score fetching.");
        return;
      }

      try {
        const response = await $fetch(`${apiUrl}sdg_predictions/publications/metrics`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
          },
          body: { publications_ids: publicationIds },
        });

        console.log("Fetched publication scores:", response);

        // Update the publications with the fetched scores
        response.forEach((metric: { publication_id: number; entropy: number }) => {
          const publication = this.selectedPublications.find(
            (pub) => pub.publication_id === metric.publication_id
          );

          if (publication) {
            publication.score = metric.entropy; // Use entropy as the score
          }
        });
      } catch (error) {
        console.error("Error fetching publication scores:", error);
        this.error = error as Error;
      }
    },

    // Synchronize selected publications with selected points
    async syncSelectedPublications() {
      const dimensionalityStore = useDimensionalityReductionsStore();
      const selectedPoints = dimensionalityStore.selectedPoints;
      console.log(selectedPoints);

      const sdgId = dimensionalityStore.getCurrentLevel;
      const levelId = dimensionalityStore.getCurrentLevel;


      if (!selectedPoints || selectedPoints.length === 0) {
        this.selectedPublications = []; // Clear if no points
        return;
      }

      // Extract publication IDs from selected points
      const selectedIds = selectedPoints
        .map((point) => point.publication_id)
        .filter((id): id is number => !!id);

      // Ensure publications for the current SDG and level are fetched
      const allPublications = this.getPublications(sdgId, levelId);

      // If publications are not yet loaded, fetch them first
      if (!allPublications || Object.keys(allPublications).length === 0) {
        console.log(`Fetching publications for SDG ${sdgId}, Level ${levelId}`);
        await this.fetchPublicationsBatch(sdgId, levelId, selectedIds); // Fetch only necessary publications
      }

      // Re-access the publications after fetching
      const levelPublications = this.getPublications(sdgId, levelId);
      this.selectedPublications = selectedIds
        .map((id) => levelPublications[id])
        .filter((pub): pub is PublicationSchemaFull => !!pub);

      console.log('Synced selected publications:', this.selectedPublications);
    },
  },
});
