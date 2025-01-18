<template>
  <div ref="rainPlotContainer" class="rain-plot">
    <!-- D3 Raincloud Plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createRaincloudPlot } from '@/composables/rainPlot';

const props = defineProps({
  width: {
    type: Number,
    required: true,
  },
  height: {
    type: Number,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
});

const rainPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (rainPlotContainer.value) {
    createRaincloudPlot(rainPlotContainer.value, props.data, {
      width: props.width,
      height: props.height,
    });
  }
});

watch([() => props.width, () => props.height, () => props.data], ([newWidth, newHeight, newData]) => {
  if (rainPlotContainer.value) {
    createRaincloudPlot(rainPlotContainer.value, newData, {
      width: newWidth,
      height: newHeight,
    });
  }
});
</script>

<style scoped>
.rain-plot {
  width: 100%;
  height: 100%;
}
</style>
