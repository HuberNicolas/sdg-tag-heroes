<template>
  <div class="flex h-full flex-row">
    <!-- Left Section -->
    <div class="relative h-full basis-1/2">
      <div class="grid grid-rows-[2fr_2fr] h-full">
        <!-- First Section: 50% -->
        <div class="row-span-1">
          <div class="flex h-full">
            <!-- First 50% of the Green Container -->
            <div class="basis-1/2 p-4">
              <p class="mb-4 text-xl font-bold">SDG-Centered</p>
              <GlyphOverview :values="values" :height="400" :width="400"></GlyphOverview>
            </div>
            <!-- Second 50% of the Green Container -->
            <div class="basis-1/2 p-4">
              <SDGExplorer></SDGExplorer>
            </div>
          </div>
        </div>

        <!-- Second Section: 50% -->
        <div class="row-span-1 flex items-center justify-center">
          <SDGUserQuery></SDGUserQuery>
        </div>
      </div>
    </div>

    <!-- Right Section -->
    <div class="flex h-full basis-1/2 flex-col items-center justify-center">
      <div v-if="!gameStore.showLeaderboard">
        <WorldSelector></WorldSelector>
      </div>
      <div v-else>
       <LeaderBoard></LeaderBoard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from "~/stores/game";
import {Stage} from "~/types/enums";
import SDGUserQuery from "~/components/SDGUserQuery.vue";

const gameStore = useGameStore();

// Values for the HexGlyph component (example)
const values = Array(17).fill(0.6);

onMounted(() => {
  gameStore.setStage(Stage.PREPARATION);
});

</script>


<style scoped>
</style>
