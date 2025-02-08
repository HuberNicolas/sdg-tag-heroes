<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-10 grid-cols-10 grid-flow-col h-full">

      <div class="row-span-10 col-span-1 bg-green-400 p-1">
        <div class="grid grid-rows-2 grid-cols-1 h-full">
          <div class="row-span-1 col-span-1 bg-purple-400">
            <BarPlot
              :width="barPlotWidth"
              :height="barPlotHeight"
            />
          </div>
          <div class="row-span-1 col-span-1 bg-orange-400">
            <div class="flex justify-center">
              <RainPlot
                :width="rainPlotWidth"
                :height="rainPlotHeight"
              />
            </div>
          </div>
        </div>
      </div>
      <div class="row-span-1 col-span-4 bg-green-400 p-1">
        <div class="grid grid-rows-2 grid-cols-6 grid-flow-col h-full">
          <div class="col-span-2 row-span-2 bg-purple-400">
            <div class="flex items-center justify-center">
              <FilterState></FilterState>
            </div>
          </div>
          <div class="col-span-4 row-span-2 bg-pink-400">
            <div class="flex items-center justify-center">
              <h1>Quests</h1>
            </div>
            <div class="flex items-center justify-around">

              <QuestButton
                icon="i-heroicons-check-badge"
                name="Confirm the King"
                tooltip="Crown the most prominent instance"
              />

              <QuestButton
                icon="i-heroicons-map"
                name="Explore"
                tooltip="Look at a variety of predictions to explore uncertainty"
              />

              <QuestButton
                icon="i-heroicons-magnifying-glass"
                name="Investigate"
                tooltip="Analyze and investigate data"
              />

              <QuestButton
                icon="i-heroicons-scale"
                name="Tiebreaker"
                tooltip="Resolve conflicts with a balanced approach"
              />
            </div>
          </div>
        </div>
      </div>
      <div class="row-span-8 col-span-4 bg-red-400 p-1">
        <div class="grid grid-rows-2 grid-cols-1 grid-flow-col h-full">
          <div class="col-span-1 row-span-1 bg-purple-400">
            <ScatterPlotSDGCollections
              v-if="selectedSDG !== null && selectedLevel !== null"
              :width="scatterPlotWidth"
              :height="scatterPlotHeight"/>
          </div>
          <div class="col-span-1 row-span-1 bg-pink-400">
            <ScatterSDGPlot
              v-if="selectedSDG !== null && selectedLevel !== null"
              :width="scatterPlotWidth"
              :height="scatterPlotHeight"/>
          </div>
        </div>
      </div>
      <div class="row-span-1 col-span-4 bg-blue-400 p-1">
        Options SDG {{selectedSDG}} - Level {{selectedLevel}}
        <ExplorationUserQuery></ExplorationUserQuery>
      </div>

      <div class="row-span-3 col-span-5 bg-blue-400 h-full overflow-auto p-1">
        <PublicationDetails></PublicationDetails>
      </div>
      <div class="row-span-6 col-span-5 bg-yellow-400 p-1">
        <PublicationsTable></PublicationsTable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ScatterSDGPlot from "~/components/plots/ScatterSDGPlot.vue";
import RainPlot from '@/components/plots/RainPlot.vue';
import BarPlot from '@/components/plots/BarPlot.vue';
import QuestButton from "~/components/QuestButton.vue";
import ExplorationUserQuery from "~/components/ExplorationUserQuery.vue";
import { ref, onMounted, watch } from 'vue';
import { useGameStore } from '~/stores/game';
import PublicationDetails from "~/components/PublicationDetails.vue";
import ScatterPlotSDGCollections from "~/components/plots/ScatterPlotSDGCollections.vue";


const route = useRoute()
const gameStore = useGameStore();

// Make as reactive
const selectedSDG = ref(null);
const selectedLevel = ref(null);


// Watch for route changes and update the store
watch(
  () => route.params,
  (params) => {
    selectedSDG.value = Number(params.sdg);
    selectedLevel.value = Number(params.level);

    // Ensure the store updates after values change
    if (selectedSDG.value && selectedLevel.value) {
      gameStore.setSDG(selectedSDG.value);
      gameStore.setLevel(selectedLevel.value);
    }
  },
  { immediate: true } // Run the watcher immediately on component mount
);


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
  }
});
</script>

<style scoped>

</style>
