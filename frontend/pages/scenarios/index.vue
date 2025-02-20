<template>
  <div class="h-full overflow-hidden">
    <div class="grid grid-rows-10 grid-cols-10 grid-flow-col h-full">

      <!-- Left Section (Takes Half of the Grid) -->
      <div class="row-span-10 col-span-5 grid grid-rows-10">

        <!-- First Section: Top Half -->
        <div class="row-span-6 grid grid-cols-2 text-center">
          <div>
            <p class="mb-4 text-xl font-bold text-white">SDG-Centered</p>
            <p class="mb-4 text-xl font-bold">Help us linking publications to SDGs</p>
          </div>


          <div class="col-span-1 p-4 flex items-center justify-center">
            <SDGExplorer />
          </div>
          <div class="col-span-1 p-4 flex flex-col items-center justify-center">
            <GlyphOverviewScenario :values="values" :height="400" :width="400" />
          </div>
        </div>

        <!-- Second Section: Bottom Half -->
        <div class="row-span-4 flex items-center justify-center">
          <SDGUserQuery />
        </div>
      </div>

      <!-- Right Section (Takes Half of the Grid) -->
      <div class="row-span-10 col-span-5 flex items-center justify-center">
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
const values = Array(17).fill(0.6);

onMounted(() => {
  gameStore.setStage(Stage.PREPARATION);
});

</script>


<style scoped>
</style>
