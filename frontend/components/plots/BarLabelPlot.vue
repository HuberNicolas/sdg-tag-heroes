<template>
  <div>
    <div ref="barPlotContainer" class="bar-plot">
      <!-- Bar plot will be rendered here -->
    </div>
    <div class="flex items-center gap-2">
      <input id="showAllVotes" type="checkbox" v-model="showAllVotes" class="h-4 w-4" />
      <label for="showAllVotes" class="text-sm font-medium">Show all votes</label>
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
});

const barPlotContainer = ref<HTMLDivElement | null>(null);
const showAllVotes = ref(false);

onMounted(() => {
  if (barPlotContainer.value) {
    createBarLabelPlot(barPlotContainer.value, props.width, props.height, showAllVotes.value);
  }
});

// Watch for changes in showAllVotes and update the chart
watch(showAllVotes, () => {
  if (barPlotContainer.value) {
    createBarLabelPlot(barPlotContainer.value, props.width, props.height, showAllVotes.value);
  }
});
</script>

<style scoped>
.bar-plot {
  height: 100%;
  width: 100%;
}
</style>
