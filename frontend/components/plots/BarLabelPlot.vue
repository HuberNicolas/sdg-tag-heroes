<!-- components/VotesBarChart.vue -->
<template>
  <div ref="barPlotContainer" class="bar-plot">
    <!-- Bar plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createBarLabelPlot } from '@/composables/plots/barLabelPlot';

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

const barPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (barPlotContainer.value) {
    createBarLabelPlot(barPlotContainer.value, props.width, props.height);
  }
});

watch([() => props.width, () => props.height], ([newWidth, newHeight]) => {
  if (barPlotContainer.value) {
    createBarLabelPlot(barPlotContainer.value, newWidth, newHeight);
  }
});
</script>

<style scoped>
.bar-plot {
  height: 100%;
  width: 100%;
}
</style>
