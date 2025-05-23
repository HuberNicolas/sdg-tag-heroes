<template>
  <div>
    <div ref="barPlotContainer" class="bar-plot">
      <div ref="chartContainer" class="chart-container"></div>
    </div>
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
  sortDescending: {
    type: Boolean,
    required: true,
  }
});

const chartContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (chartContainer.value) {
    createBarLabelPlot(chartContainer.value, props.width, props.height, props.sortDescending);
  }
});

watch(() => props.sortDescending, (newVal) => {
  if (chartContainer.value) {
    createBarLabelPlot(chartContainer.value, props.width, props.height, newVal);
  }
});
</script>

<style scoped>
.bar-plot {
  height: 100%;
  width: 100%;
}
</style>
