<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-6 grid-cols-6 grid-flow-col h-full">
      <div class="row-span-5 col-span-5 bg-red-400 relative">
        <ScatterPlot :width="scatterWidth" :height="scatterHeight" />
        <div class="absolute top-0 left-0 w-1/3 h-1/3">
          <RainPlot :width="rainPlotWidth" :height="rainPlotHeight" :data="[10, 20, 15, 25, 18, 30]" />
        </div>
      </div>
      <div class="row-span-1 col-span-5 bg-blue-400">Options</div>
      <div class="row-span-1 col-span-2 bg-green-400">Quests (Entropy Based)</div>
      <div class="row-span-5 col-span-2 bg-yellow-400">
        <PublicationsTable></PublicationsTable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ScatterPlot from '@/components/ScatterPlot.vue';
import RainPlot from '@/components/RainPlot.vue';
import { ref, onMounted } from 'vue';

const route = useRoute();
const selectedLevel = route.params.level;

// Track dimensions for ScatterPlot
const scatterWidth = ref(0);
const scatterHeight = ref(0);
const rainPlotWidth = ref(0);
const rainPlotHeight = ref(0);



onMounted(() => {
  const container = document.querySelector('.row-span-5.col-span-5'); // Select the red container
  if (container) {
    scatterWidth.value = container.clientWidth;
    scatterHeight.value = container.clientHeight;

    rainPlotWidth.value = container.clientWidth / 3; // 1/3 of container width
    rainPlotHeight.value = container.clientHeight / 3; // 1/3 of container height
  }
});
</script>
