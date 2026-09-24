<template>
  <div class="frame-container flex flex-col">
    <div class="frame-title flex-none"><b>Explore</b> Publications Using the <b>Publication Map</b>: Use Brushing, Hovering, Lasso-Selection and clicking to Discover Patterns in the Dataset</div>
    <div ref="scatterPlotContainer" class="flex-1 min-h-0 w-full">
      <!-- Plotly scatter plot is rendered here -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Plotly from 'plotly.js-dist';
import { createScatterPlot } from '@/composables/plots/scatterPlot';

const scatterPlotContainer = ref<HTMLDivElement | null>(null);
const mapPartitions = Number(useRuntimeConfig().public.mapPartitions) || 1000;

onMounted(() => {
  if (scatterPlotContainer.value) {
    createScatterPlot(scatterPlotContainer.value, undefined, undefined, 'top1', mapPartitions);
  }
});

// Keep the plot the size of its container (window resize, panels growing or shrinking)
useRedrawOnResize(scatterPlotContainer, () => {
  if (scatterPlotContainer.value?.querySelector('.plot-container')) {
    Plotly.Plots.resize(scatterPlotContainer.value);
  }
}, { trackHeight: true });
</script>
