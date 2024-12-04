<template>
  <div ref="hexGridContainer" class="hex-grid"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import useHexGrid from '@/composables/useHexGrid';
import { usePredictionsStore } from "~/stores/sdg_predictions";
import { usePublicationsStore } from "~/stores/publications";

const predictionsStore = usePredictionsStore();
const publicationsStore = usePublicationsStore();

const hexGridContainer = ref<HTMLDivElement | null>(null);
let isRendered = false; // Flag to ensure `renderHexGrid` is called only once

// Watch for the selected publication and trigger predictions fetch
watch(
  () => publicationsStore.selectedPublication,
  async (newPublication) => {
    if (newPublication && newPublication.publication_id) {
      try {
        await predictionsStore.fetchPredictionsByPublicationId(newPublication.publication_id);
        if (!isRendered && hexGridContainer.value) {
          const values = extractPredictionValues(predictionsStore.selectedPublicationPrediction);
          // Invert each value: 1 - value
          const invertedValues = values.map(value => 1 - value);
          const { renderHexGrid } = useHexGrid(invertedValues);
          renderHexGrid(hexGridContainer.value);
          isRendered = true;
        }
      } catch (error) {
        console.error("Error fetching predictions:", error);
      }
    }
  },
  { immediate: true } // Trigger immediately in case the selected publication is already available
);

function extractPredictionValues(prediction): number[] {
  if (!prediction) {
    return [];
  }

  // Extract values for SDG goals (sdg1 to sdg17)
  const sdgKeys = Array.from({ length: 17 }, (_, i) => `sdg${i + 1}`);
  const sdgValues = sdgKeys.map((key) => (prediction as any)[key]);

  // Ensure all values are numbers and handle potential null or undefined
  return sdgValues.map((value) => (typeof value === 'number' ? value : 0));
}


// Optional cleanup
onUnmounted(() => {
  if (hexGridContainer.value) {
    hexGridContainer.value.innerHTML = ''; // Clear the container
  }
});
</script>

<style scoped>
.hex-grid {
  width: 100%;
  height: 100%;
}
</style>
