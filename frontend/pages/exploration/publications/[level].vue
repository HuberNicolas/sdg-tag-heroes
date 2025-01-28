<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-8 grid-cols-6 grid-flow-col h-full">
      <div class="row-span-6 col-span-4 bg-red-400">
        <ScatterPlot :width="scatterPlotWidth" :height="scatterPlotHeight"/>
      </div>
      <div class="row-span-2 col-span-4 bg-blue-400">
        Options Level {{selectedLevel}}
        <!-- Add h-full to ensure the grid takes full height -->
        <div class="grid grid-cols-3 h-full">
          <div class="col-span-1 bg-purple-400">
            <BarPlot
              :width="barPlotWidth"
              :height="barPlotHeight"
            />
          </div>
          <div class="col-span-1 bg-orange-400">
            <div class="flex justify-center">
              <RainPlot
                :width="rainPlotWidth"
                :height="rainPlotHeight"
              />
            </div>
          </div>
          <div class="col-span-1 bg-purple-400">
            <div class="flex justify-center">
              <div>Queries</div>
            </div>
          </div>
        </div>
      </div>
      <div class="row-span-1 col-span-2 bg-green-400 p-4">
        <div class="flex items-center justify-center">
          <h1>Quests</h1>
        </div>
        <div class="flex items-center justify-between">
          <ButtonsQuestButton :mode="'1'" />
          <ButtonsQuestButton :mode="'2'" />
          <ButtonsQuestButton :mode="'3'" />
          <ButtonsQuestButton :mode="'4'" />
          <ButtonsQuestButton :mode="'5'" />
        </div>

      </div>
      <div class="row-span-7 col-span-2 bg-yellow-400">
        <PublicationsTable></PublicationsTable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ScatterPlot from '@/components/plots/ScatterPlot.vue';
import RainPlot from '@/components/plots/RainPlot.vue';
import BarPlot from '@/components/plots/BarPlot.vue';
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

onMounted(() => {
  const mapContainer = document.querySelector('.row-span-4.col-span-4');
  if (mapContainer) {
    scatterPlotWidth.value = mapContainer.clientWidth;
    scatterPlotHeight.value = mapContainer.clientHeight;
  }

  const optionContainer = document.querySelector('.row-span-2.col-span-4');
  if (optionContainer) {
    barPlotWidth.value = optionContainer.clientWidth / 6;
    barPlotHeight.value = optionContainer.clientHeight / 6;

    rainPlotWidth.value = optionContainer.clientWidth / 3; // 1/3 of container width
    rainPlotHeight.value = optionContainer.clientHeight / 3; // 1/3 of container height
    console.log(barPlotWidth.value, barPlotHeight.value);
  }
});
</script>

<style scoped>

</style>
