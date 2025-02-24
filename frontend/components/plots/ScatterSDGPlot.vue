<template>
  <div class="frame-title"><b>Explore</b> Publications Using the <b>Interactive Scatter Plot</b>:Use Brushing, Hovering, Lasso-Selection and clicking to Discover Patterns in the Dataset</div>
  <div ref="scatterPlotContainer" class="scatter-plot">
    <!-- D3 Scatter Plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createScatterPlot } from '@/composables/plots/scatterSDGPlot';

const props = defineProps({
  width: {
    type: Number,
    required: true,
  },
  height: {
    type: Number,
    required: true,
  },
});

const scatterPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (scatterPlotContainer.value) {
    createScatterPlot(scatterPlotContainer.value, props.width, props.height);
  }
});

watch([() => props.width, () => props.height], ([newWidth, newHeight]) => {
  if (scatterPlotContainer.value) {
    createScatterPlot(scatterPlotContainer.value, newWidth, newHeight);
  }
});
</script>

<style scoped>
.scatter-plot {
  width: 100%;
  height: 100%;
}
</style>
