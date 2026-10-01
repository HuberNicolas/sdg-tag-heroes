<template>
  <!-- From xl on, the page fills the window: a strip of filters on top, below it the big publication map
       (left) and the summary with the table (right). Below xl, the panels stack and the page scrolls. -->
  <div class="min-h-full xl:h-full flex flex-col gap-3 p-3">
    <section class="flex-none">
      <p class="kicker mb-2">// find a set of interesting publications</p>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <CollectionSelector />
        <QuestSection />
        <ExplorationUserQuery />
      </div>
    </section>

    <div class="flex-1 min-h-0 grid grid-cols-1 xl:grid-cols-12 gap-3">
      <ScatterSDGPlot
        v-if="selectedSDG !== null && selectedLevel !== null"
        class="xl:col-span-7 min-h-[34rem] xl:min-h-0"
      />

      <!-- Summary of the selection and the publication table -->
      <div class="xl:col-span-5 flex flex-col gap-3 min-h-0">
        <div class="flex-none">
          <div class="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1.5">
            <p class="kicker">// summarize your selection</p>
            <SelectionTrail />
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-5 gap-3">
            <div class="lg:col-span-2 flex flex-col gap-3">
              <FilterState />
              <BarPlot />
            </div>
            <div class="lg:col-span-3">
              <RainPlotExploration />
            </div>
          </div>
        </div>

        <PublicationsTable class="flex-1 min-h-[20rem]" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SelectionTrail from "~/components/SelectionTrail.vue";
import ScatterSDGPlot from "~/components/plots/ScatterSDGPlot.vue";
import BarPlot from "@/components/plots/BarPlot.vue";
import ExplorationUserQuery from "~/components/ExplorationUserQuery.vue";
import { onMounted, ref, watch } from "vue";
import { useGameStore } from "~/stores/game";
import { Quadrant, Stage } from "~/types/enums";
import QuestSection from "~/components/QuestSection.vue";
import RainPlotExploration from "~/components/plots/RainPlotExploration.vue";


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



onMounted(() => {
  gameStore.setQuadrant(Quadrant.MANY_PUBS_ONE_SDG);
  gameStore.setStage(Stage.EXPLORING);
});
</script>

<style scoped>

</style>
