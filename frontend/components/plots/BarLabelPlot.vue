<template>
  <div>
    <div ref="barPlotContainer" class="bar-plot">
      <div ref="chartContainer" class="chart-container"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createBarLabelPlot } from '@/composables/plots/barLabelPlot';

const props = defineProps({
  // Leave out to use the width of the container
  width: {
    type: Number,
    default: 0,
  },
  height: {
    type: Number,
    required: true,
  },
  sortDescending: {
    type: Boolean,
    required: true,
  }
});

const chartContainer = ref<HTMLDivElement | null>(null);
let redraw: (() => void) | null = null;

onMounted(() => {
  if (chartContainer.value) {
    redraw = createBarLabelPlot(chartContainer.value, props.width, props.height, props.sortDescending).updateChart;
  }
});

watch(() => props.sortDescending, (newVal) => {
  if (chartContainer.value) {
    redraw = createBarLabelPlot(chartContainer.value, props.width, props.height, newVal).updateChart;
  }
});

useRedrawOnResize(chartContainer, () => redraw?.());
</script>

<style scoped>
.bar-plot {
  height: 100%;
  width: 100%;
}
</style>
