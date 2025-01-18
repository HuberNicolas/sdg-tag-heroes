<template>
  <div ref="barPlotContainer" class="bar-plot">
    <!-- Bar plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createBarPlot } from '@/composables/barPlot';

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
    type: Array as () => { x: string[]; y: number[]; }[],
    required: true,
  },
});

const barPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (barPlotContainer.value) {
    createBarPlot(barPlotContainer.value, props.width, props.height, props.data);
  }
});

watch([() => props.width, () => props.height, () => props.data,], ([newWidth, newHeight, newData,]) => {
  if (barPlotContainer.value) {
    createBarPlot(barPlotContainer.value, newWidth, newHeight, newData,);
  }
});
</script>

<style scoped>
.bar-plot {
  width: 100%;
  height: 100%;
}
</style>
