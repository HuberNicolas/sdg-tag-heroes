<template>
  <div ref="barPlotContainer" class="bar-plot">
    <!-- Bar plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createBarPlot } from '@/composables/plots/barPlot';

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
    createBarPlot(barPlotContainer.value, props.width, props.height);
  }
});

watch([() => props.width, () => props.height,], ([newWidth, newHeight,]) => {
  if (barPlotContainer.value) {
    createBarPlot(barPlotContainer.value, newWidth, newHeight,);
  }
});
</script>
