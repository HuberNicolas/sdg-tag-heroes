<template>
  <div ref="rainPlotContainer" class="rain-plot">
    <!-- D3 Raincloud Plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createRaincloudPlot } from '@/composables/plots/rainPlot';

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

const rainPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (rainPlotContainer.value) {
    createRaincloudPlot(rainPlotContainer.value, props.width, props.height,)
  }
});

watch([() => props.width, () => props.height,], ([newWidth, newHeight]) => {
  if (rainPlotContainer.value) {
    createRaincloudPlot(rainPlotContainer.value, newWidth, newHeight,);
  }
});
</script>
