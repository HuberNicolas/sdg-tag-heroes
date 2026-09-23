<template>
  <!-- From xl on, the page fills the window: map and table take the remaining height.
       Below xl, the panels stack and the page scrolls. -->
  <div class="min-h-full xl:h-full grid grid-cols-1 xl:grid-cols-2 gap-3 p-3">
    <!-- Left: find publications and explore the map -->
    <div class="flex flex-col gap-3 min-h-0">
      <div class="flex-none">
        <div class="frame-title"><b>Find a set of interesting publications: </b></div>
        <CollectionSelector />
        <div class="mt-3 grid grid-cols-1 2xl:grid-cols-5 gap-3">
          <QuestSectionPublications class="2xl:col-span-3" />
          <ExplorationUserQuery class="2xl:col-span-2" />
        </div>
      </div>

      <ScatterPlot
        v-if="selectedLevel !== null"
        class="flex-1 min-h-[18rem]"
      />

      <ScatterPlotExplorationLegend class="flex-none" />
    </div>

    <!-- Right: summary of the selection and the publication table -->
    <div class="flex flex-col gap-3 min-h-0">
      <div class="flex-none">
        <div class="frame-title"><b>Summarize</b> Your Selection: Explore Machine Label Predictions & XP Distribution in the <b>Summary Panel</b></div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <div class="flex flex-col gap-3">
            <FilterStateExploration />
            <BarPlot />
          </div>
          <div class="lg:col-span-2">
            <RainPlotExploration />
          </div>
        </div>
      </div>

      <PublicationsTableExploration class="flex-1 min-h-[20rem]" />
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



onMounted(() => {
  gameStore.setQuadrant(Quadrant.MANY_PUBS_ALL_SDG);
  gameStore.setStage(Stage.EXPLORING);
});
</script>

<style scoped>

</style>
