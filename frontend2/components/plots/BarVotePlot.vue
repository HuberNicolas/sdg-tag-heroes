<template>
  <div ref="barPlotContainer" class="bar-plot">
    <!-- Bar plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { createBarVotePlot } from '@/composables/plots/barVotePlot';

const props = defineProps({
  width: {
    type: Number,
    required: true,
  },
  height: {
    type: Number,
    required: true,
  },
  votesData: {
    type: Object,
    required: true,
  }
});

const barPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (barPlotContainer.value) {
    createBarVotePlot(barPlotContainer.value, props.width, props.height, props.votesData);
  }
});

watch(() => props.votesData, (newVotesData) => {
  if (barPlotContainer.value) {
    createBarVotePlot(barPlotContainer.value, props.width, props.height, newVotesData);
  }
}, { deep: true });
</script>

<style scoped>
.bar-plot {
  height: 100%;
  width: 100%;
}
</style>
