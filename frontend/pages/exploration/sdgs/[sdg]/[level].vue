<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-8 grid-cols-6 grid-flow-col h-full">
      <div class="row-span-6 col-span-4 bg-red-400">
        <ScatterSDGPlot :width="scatterPlotWidth" :height="scatterPlotHeight"/>
      </div>
      <div class="row-span-2 col-span-4 bg-blue-400">
        Options SDG {{selectedSDG}} - Level {{selectedLevel}}
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
            <ExplorationUserQuery></ExplorationUserQuery>
          </div>
        </div>
      </div>
      <div class="row-span-1 col-span-2 bg-green-400 p-4">

        <div class="grid grid-rows-2 grid-cols-6 grid-flow-col h-full">

          <div class="col-span-2 row-span-2 bg-purple-400">
            <div class="flex items-center justify-center">
              <h1>Quests</h1>
            </div>
            <div class="flex items-center justify-around">
              <QuestButton
                icon="i-heroicons-light-bulb"
                name="Label Sparse Instances"
                tooltip="Label an instance with the least annotations"
              />

              <QuestButton
                icon="i-heroicons-fire"
                name="High Stakes"
                tooltip="Sort the most uncertain instances based on entropy"
              />
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
      <div class="row-span-7 col-span-2 bg-yellow-400">
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
import { ref, onMounted } from 'vue';
import { useSDGsStore } from '~/stores/sdgs';
import { useGameStore } from '~/stores/game';



const route = useRoute()


const selectedSDG = route.params.sdg as Number
const selectedLevel = route.params.level as Number

const sdgsStore = useSDGsStore();
const gameStore = useGameStore();

// Set the selectedSDG and selectedLevel in the stores
onMounted(() => {
  sdgsStore.setSelectedSDG(selectedSDG);
  gameStore.setLevel(selectedLevel);
});



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
