<template>
  <div class="flex-1  h-full overflow-hidden">
    <!--
      <div class="row-span-4 col-span-5  h-full overflow-auto p-1">
        <PublicationDetails></PublicationDetails>
      </div>
      -->

    <div class="grid grid-rows-12 grid-cols-10 h-full">
      <div class="row-span-5 col-span-5 p-1">

        <div class="grid grid-rows-10 grid-cols-6 h-full gap-0">

          <div class="row-span-6 col-span-6">
            <div class="frame-title"><b>Find a set of interesting publications: </b></div>
            <CollectionSelector></CollectionSelector>
          </div>
          <div class="row-span-2 col-span-4">
            <QuestSectionPublications></QuestSectionPublications>
          </div>
          <div class="row-span-2 col-span-2">
            <ExplorationUserQuery></ExplorationUserQuery>
          </div>
        </div>
      </div>

    <div class="row-span-4 col-span-5 p-1">
        <div class="grid grid-rows-11 grid-cols-3 h-full">
          <div class="row-span-1 col-span-3 "> <div class="frame-title"><b>Summarize</b> Your Selection: Explore Machine Label Predictions & XP Distribution in the <b>Summary Panel</b></div></div>
          <div class="row-span-5 col-span-1 ">
            <div class="flex justify-center">
              <FilterStateExploration></FilterStateExploration>
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
        <PublicationsTableExploration></PublicationsTableExploration>
      </div>

      <div class="row-span-5 col-span-5 p-1">
        <ScatterPlot
          v-if="selectedLevel !== null"
          :width="scatterPlotWidth"
          :height="scatterPlotHeight"/>
      </div>

      <div class="col-span-5 p-1">
        <ScatterPlotExplorationLegend></ScatterPlotExplorationLegend>
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
import ScatterPlot from "~/components/plots/ScatterPlot.vue";
import PublicationsTableExploration from "~/components/PublicationsTableExploration.vue";
import RainPlotExploration from "~/components/plots/RainPlotExploration.vue";
import ScatterPlotLegend from "~/components/ScatterPlotLegend.vue";
import ScatterPlotExplorationLegend from "~/components/ScatterPlotExplorationLegend.vue";


const route = useRoute()
const gameStore = useGameStore();

// Make as reactive
const selectedLevel = ref(null);


// Watch for route changes and update the store
watch(
  () => route.params,
  (params) => {
    selectedLevel.value = Number(params.level);

    // Ensure the store updates after values change
    if (selectedLevel.value) {
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
  gameStore.setQuadrant(Quadrant.MANY_PUBS_ALL_SDG);
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
