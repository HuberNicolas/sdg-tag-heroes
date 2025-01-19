<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-6 grid-cols-6 grid-flow-col h-full">
      <div class="row-span-4 col-span-4 bg-red-400">
        <ScatterPlot :width="scatterPlotWidth" :height="scatterPlotHeight" />
      </div>
      <div class="row-span-2 col-span-4 bg-blue-400">
        Options Level {{selectedLevel}}
        <div class="grid grid-cols-2 gap-4">
          <div class="col-span-1">
            <BarPlot
            :width="barPlotWidth"
            :height="barPlotHeight"
            :data="barPlotData"
            />
          </div>
          <div class="col-span-1">
            <RainPlot :width="rainPlotWidth" :height="rainPlotHeight" :data="[10, 20, 15, 25, 18, 30]" />
          </div>
        </div>
      </div>
      <div class="row-span-1 col-span-2 bg-green-400 p-4">
        <div class="grid grid-cols-3 gap-4">
          <!-- Title -->
          <div class="col-span-3 grid grid-cols-1 gap-4">
            <p>Quests</p>
          </div>

          <!-- Left side (2x2 grid for buttons 1-4) -->
          <div class="col-span-2 grid grid-cols-2 gap-4">
            <ButtonsQuestButton :mode="'1'" />
            <ButtonsQuestButton :mode="'2'" />
            <ButtonsQuestButton :mode="'3'" />
            <ButtonsQuestButton :mode="'4'" />
          </div>

          <!-- Right side (button 5) -->
          <div class="flex items-center justify-center">
            <ButtonsQuestButton :mode="'5'" />
          </div>
        </div>

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
  const mapContainer = document.querySelector('.row-span-4.col-span-4');
  if (mapContainer) {
    scatterPlotWidth.value = mapContainer.clientWidth;
    scatterPlotHeight.value = mapContainer.clientHeight;
  }

  const optionContainer = document.querySelector('.row-span-2.col-span-4');
  if (optionContainer) {
    barPlotWidth.value = optionContainer.clientWidth / 3;
    barPlotHeight.value = optionContainer.clientHeight / 2;

    rainPlotWidth.value = optionContainer.clientWidth / 3; // 1/3 of container width
    rainPlotHeight.value = optionContainer.clientHeight / 3; // 1/3 of container height
    console.log(barPlotWidth.value, barPlotHeight.value);
  }
});
</script>
