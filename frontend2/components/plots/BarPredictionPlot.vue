<template>
  <div ref="barPlotContainer" class="bar-plot">
    <!-- Bar plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createBarPlot } from '@/composables/plots/barPredictionPlot';

const props = defineProps({
  values: {
    type: Array as PropType<number[]>,
    required: true,
    default: () => Array(17).fill(0), // Default to an array of 17 zeros
    validator: (arr: number[]) => arr.length === 17, // Ensure 17 values
  },
  width: {
    type: Number,
    required: true,
  },
  height: {
    type: Number,
    required: true,
  },
});

const barPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (barPlotContainer.value) {
    createBarPlot(barPlotContainer.value, props.values, props.width, props.height);
  }
});

watch(
  [() => props.values, () => props.width, () => props.height],
  ([newValues, newWidth, newHeight]) => {
    if (barPlotContainer.value) {
      createBarPlot(barPlotContainer.value, newValues, newWidth, newHeight);
    }
  }
);
</script>

<style scoped>
.bar-plot {
  width: 100%;
  height: 100%;
}
</style>
