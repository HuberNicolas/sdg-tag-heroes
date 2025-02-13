<template>
  <div class="flex flex-col h-screen overflow-auto">


    <div class="grid grid-rows-10 grid-cols-10 h-full">


      <div class="row-span-3 col-span-5 p-1">


        <div class="grid grid-rows-6 grid-cols-6 grid-flow-col h-full">


          <div class="row-span-4 col-span-6">
            <CollectionSelector></CollectionSelector>
          </div>



          <div class="row-span-2 col-span-3">
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

          <div class="row-span-2 col-span-3">
            <ExplorationUserQuery></ExplorationUserQuery>
          </div>
        </div>



      </div>

      <div class="row-span-6 col-span-5 p-1">
        <PublicationsTable></PublicationsTable>
      </div>

      <div class="row-span-4 col-span-5 p-1">
        <ScatterSDGPlot
          v-if="selectedSDG !== null && selectedLevel !== null"
          :width="scatterPlotWidth"
          :height="scatterPlotHeight"/>
      </div>

      <div class="row-span-4 col-span-5  h-full overflow-auto p-1">
        <PublicationDetails></PublicationDetails>
      </div>

      <div class="row-span-3 col-span-5  p-1">

        <div class="grid grid-rows-2 grid-cols-3 h-full">
          <div class="row-span-1 col-span-1 ">
            <div class="flex justify-center">
              <FilterState></FilterState>
            </div>
          </div>
          <div class="row-span-2 col-span-2 ">
            <div class="flex justify-center">
              <RainPlot />
            </div>
          </div>
          <div class="row-span-1 col-span-1 ">
            <BarPlot />
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ScatterSDGPlot from "~/components/plots/ScatterSDGPlot.vue";
import RainPlot from "@/components/plots/RainPlot.vue";
import BarPlot from "@/components/plots/BarPlot.vue";
import QuestButton from "~/components/QuestButton.vue";
import ExplorationUserQuery from "~/components/ExplorationUserQuery.vue";
import { onMounted, ref, watch } from "vue";
import { useGameStore } from "~/stores/game";
import PublicationDetails from "~/components/PublicationDetails.vue";
import { Quadrant, Stage } from "~/types/enums";


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
  gameStore.setQuadrant(Quadrant.MANY_PUBS_ONE_SDG);
  gameStore.setStage(Stage.EXPLORING);
  const mapContainer = document.querySelector('.row-span-4.col-span-4');
  if (mapContainer) {
    scatterPlotWidth.value = mapContainer.clientWidth;
    scatterPlotHeight.value = mapContainer.clientHeight;
  }

  const optionContainer = document.querySelector('.row-span-2.col-span-4');
  if (optionContainer) {
    barPlotWidth.value = optionContainer.clientWidth;
    barPlotHeight.value = optionContainer.clientHeight;

    rainPlotWidth.value = optionContainer.clientWidth / 3; // 1/3 of container width
    rainPlotHeight.value = optionContainer.clientHeight / 3; // 1/3 of container height
  }
});
</script>

<style scoped>

</style>
