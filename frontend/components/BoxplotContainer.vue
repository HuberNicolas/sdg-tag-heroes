<template>
  <div class="boxplot-container">
    <div
      v-for="(boxplot, index) in boxplotData"
      :key="index"
      :id="`boxplot-${index}`"
      class="boxplot"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { usePublicationStore } from '~/stores/publications'; // Import the Pinia store
import { createBoxPlot } from '~/composables/boxPlot';

// Access the store
const store = usePublicationStore();

// Transform the selected data into arrays for x, y, and score
const boxplotData = computed(() => {
  const selectedPoints = store.selectedPoints;
  const xValues = selectedPoints.map(point => point.x);
  const yValues = selectedPoints.map(point => point.y);
  const scores = selectedPoints.map(point => point.score);

  return [xValues, yValues, scores];
});

// Options for box plot dimensions
const options = {
  width: 200,
  height: 200,
};

// Watch for changes in boxplotData and update the box plots
watch(
  boxplotData,
  (newData) => {
    // Clear existing box plots before creating new ones
    newData.forEach((data, index) => {
      const containerId = `boxplot-${index}`;
      createBoxPlot(containerId, data, options);
    });
  },
  { immediate: true } // Run the watch effect immediately on component mount
);
</script>

<style scoped>
.boxplot-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.boxplot {
  width: 100%;
  height: 400px;
}
</style>
