<template>
  <div class="flex-1 h-full overflow-hidden">


    <div class="grid grid-rows-12 grid-cols-10 h-full">
        <div class="row-span-5 col-span-5 p-1">

          <div class="grid grid-rows-10 grid-cols-6 h-full gap-0">
            <div class="row-span-6 col-span-6">
              <div class="frame-title"><b>Find a set of interesting publications: </b></div>
              <CollectionSelector></CollectionSelector>
            </div>
            <div class="row-span-2 col-span-3">
              <QuestSection></QuestSection>
            </div>
            <div class="row-span-2 col-span-3">
              <ExplorationUserQuery></ExplorationUserQuery>
            </div>
          </div>
        </div>

        <div class="row-span-4 col-span-5 p-1">
          <div class="grid grid-rows-11 grid-cols-3 h-full">
            <div class="row-span-1 col-span-3 "> <div class="frame-title"><b>Summarize</b> Your Selection: Explore Machine Label Predictions & XP Distribution</div></div>
            <div class="row-span-5 col-span-1 ">
              <div class="flex justify-center">
                <FilterState></FilterState>
              </div>
            </div>
            <div class="row-span-10 col-span-2 ">
              <div class="flex justify-center">
                <RainPlotExploration />
              </div>
            </div>
            <div class="row-span-5 col-span-1 ">
              <BarPlot />
            </div>
          </div>
        </div>

        <div class="row-span-9 col-span-5 p-1">
          <PublicationsTable></PublicationsTable>
        </div>

        <div class="row-span-5 col-span-5 p-1">
          <ScatterSDGPlot
            v-if="selectedSDG !== null && selectedLevel !== null"
            :width="scatterPlotWidth"
            :height="scatterPlotHeight"/>
        </div>

      <div class="col-span-5 p-1">
        <ScatterPlotLegend></ScatterPlotLegend>
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
import QuestSection from "~/components/QuestSection.vue";
import PublicationsTableExploration from "~/components/PublicationsTableExploration.vue";
import ScatterPlotExplorationLegend from "~/components/ScatterPlotExplorationLegend.vue";
import RainPlotExploration from "~/components/plots/RainPlotExploration.vue";
import ScatterPlot from "~/components/plots/ScatterPlot.vue";


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
