<template>
  <div class="h-full overflow-hidden">
    <div class="grid grid-rows-11 grid-cols-10 grid-flow-col h-full">

      <!-- Title Section (Spanning Across All Columns) -->
      <div class="row-span-1 col-span-10 flex flex-col items-center justify-center text-center p-4 bg-gray-50">
        <h1 class="text-3xl font-bold w-full">
          Wanna be an SDG-Tag Hero? Then help us linking Publications with SDGs either
        </h1>
        <div class="w-full flex justify-center mt-2 items-center">
          <div class="w-1/3 flex items-center justify-center">
            <p class="text-xl">by <b>Selecting</b> an SDG</p>
          </div>
          <div class="w-auto px-4 text-xl font-bold text-gray-700">OR</div>
          <div class="w-1/3 flex items-center justify-center">
            <p class="text-xl">by <b>Exploring</b> Publications from different Worlds</p>
          </div>
        </div>
      </div>


      <!-- Left Section (Takes Half of the Grid) -->
      <div class="row-span-10 col-span-5 grid grid-rows-10">


        <!-- First Section: Top Half -->
        <div class="row-span-7 grid grid-cols-2 text-center">
          <div class="col-span-1 p-4 flex items-center justify-center">
            <GlyphOverviewScenario :values="values" :height="400" :width="400" />
          </div>

          <div class="col-span-1 p-4 flex flex-col items-center justify-center">
            <SDGExplorer />
          </div>
        </div>

        <!-- Second Section: Bottom Half -->
        <div v-if="!gameStore.showLeaderboard" class="row-span-3 flex items-center justify-center">
          <SDGUserQuery />
        </div>
        <div v-if="gameStore.showLeaderboard" class="row-span-3 flex items-center justify-center">
          <LeaderBoardExplanation></LeaderBoardExplanation>
        </div>
      </div>

      <!-- Right Section (Takes Half of the Grid) -->
      <div class="row-span-10 col-span-5 flex items-center justify-center border-l-8 border-gray-500 relative">
        <span class="absolute top-1/2 right-full transform translate-x-8 -translate-y-1/2 px-6 py-3 text-gray-700 text-sm font-bold"></span>
        <div v-if="!gameStore.showLeaderboard" class="w-full h-full flex items-center justify-center">
          <WorldSelector />
        </div>
        <div v-else class="w-full h-full flex items-center justify-center">
          <LeaderBoard />
        </div>
      </div>

    </div>
  </div>
</template>


<script setup lang="ts">
import { useGameStore } from "~/stores/game";
import {Stage} from "~/types/enums";
import SDGUserQuery from "~/components/SDGUserQuery.vue";
import GlyphOverviewScenario from "~/components/GlyphOverviewScenario.vue";

const gameStore = useGameStore();

// Values for the HexGlyph component (example)
const values = Array(17).fill(1);

onMounted(() => {
  gameStore.setStage(Stage.PREPARATION);
});

</script>


<style scoped>
</style>
