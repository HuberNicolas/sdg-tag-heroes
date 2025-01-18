<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-6 grid-cols-6 grid-flow-col h-full">
      <div class="row-span-5 col-span-5 bg-red-400 relative">
        <ScatterPlot :width="scatterPlotWidth" :height="scatterPlotHeight" />
        <div class="absolute top-0 left-0 w-1/3 h-1/3">
          <RainPlot :width="rainPlotWidth" :height="rainPlotHeight" :data="[10, 20, 15, 25, 18, 30]" />
        </div>
      </div>
      <div class="row-span-1 col-span-5 bg-blue-400">
        Options
        <BarPlot
          :width="barPlotWidth"
          :height="barPlotHeight"
          :data="barPlotData"
        />
      </div>
      <div class="row-span-1 col-span-2 bg-green-400">
        Quests (Entropy Based)
        <ButtonsQuestButton :name="'Tip the scale'" :mode="'1'"></ButtonsQuestButton>
        <ButtonsQuestButton :name="'Tip the scale'" :mode="'2'"></ButtonsQuestButton>
        <ButtonsQuestButton :name="'Tip the scale'" :mode="'3'"></ButtonsQuestButton>
        <ButtonsQuestButton :name="'Tip the scale'" :mode="'4'"></ButtonsQuestButton>
        <ButtonsQuestButton :name="'Tip the scale'" :mode="'5'"></ButtonsQuestButton>

      </div>
      <div class="row-span-5 col-span-2 bg-yellow-400">
        <PublicationsTable></PublicationsTable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ScatterPlot from '@/components/ScatterPlot.vue';
import RainPlot from '@/components/RainPlot.vue';
import BarPlot from '@/components/BarPlot.vue';
import { ref, onMounted } from 'vue';

const route = useRoute();
const selectedLevel = route.params.level;

// Track dimensions for ScatterPlot
const scatterPlotWidth = ref(0);
const scatterPlotHeight = ref(0);

const rainPlotWidth = ref(0);
const rainPlotHeight = ref(0);

const barPlotWidth = ref(0);
const barPlotHeight = ref(0);

const barPlotData = ref([
  {
    x: Array.from({ length: 17 }, (_, i) => `SDG${i + 1}`),
    y: Array.from({ length: 17 }, () => Math.floor(Math.random() * 100) + 1),
  },
]);

onMounted(() => {
  const mapContainer = document.querySelector('.row-span-5.col-span-5'); // Select the map container
  if (mapContainer) {
    scatterPlotWidth.value = mapContainer.clientWidth;
    scatterPlotHeight.value = mapContainer.clientHeight;

    rainPlotWidth.value = mapContainer.clientWidth / 3; // 1/3 of container width
    rainPlotHeight.value = mapContainer.clientHeight / 3; // 1/3 of container height
  }

  const optionContainer = document.querySelector('.row-span-1.col-span-5');
  if (optionContainer) {
    barPlotWidth.value = optionContainer.clientWidth / 3;
    barPlotHeight.value = optionContainer.clientHeight / 2;
  }
});
</script>
