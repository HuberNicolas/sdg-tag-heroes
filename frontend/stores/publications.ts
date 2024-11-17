import { defineStore } from 'pinia';
import type { PublicationSchema } from '@/types/schemas'; // Import your PublicationSchema type

// Define a Pinia store for managing publications
export const usePublicationStore = defineStore('publications', {
  state: () => ({
    count: 0, // Initial state for count
    selectedPoints: [], // Array to hold selected data points
    publications: [] as PublicationSchema[], // Array to hold loaded publications
    loading: false, // State to indicate loading status
    error: null as string | null // State to hold any error messages
  }),

  actions: {
    // Action to increment the count
    increment() {
      this.count++;
    },

    // Action to add points to the selection
    addSelectedPoints(newPoints) {
      this.selectedPoints = [...this.selectedPoints, ...newPoints];
    },

    // Action to clear selected points
    clearSelectedPoints() {
      this.selectedPoints = [];
    },

    // Action to set selected points (useful for brushing)
    setSelectedPoints(points) {
      this.selectedPoints = points;
    },

    // Action to load and store publications
    async loadPublications(fetchPublicationsFn: () => Promise<PublicationSchema[]>) {
      this.loading = true;
      this.error = null;
      try {
        const publications = await fetchPublicationsFn();
        this.publications = publications;
      } catch (err: any) {
        this.error = err.message || 'Failed to load publications';
        console.error('Error loading publications:', err);
      } finally {
        this.loading = false;
      }
    },

    // Action to clear publications from the store
    clearPublications() {
      this.publications = [];
    }
  }
});
