import { defineStore } from 'pinia';

// Define a Pinia store for managing selected points
export const usePublicationStore = defineStore('publications', {
  state: () => ({
    count: 0, // Initial state for count
    selectedPoints: [] // Array to hold selected data points
  }),

  actions: {
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
    }
  }
});
