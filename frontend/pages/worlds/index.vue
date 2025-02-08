<template>
  <div class="flex h-full flex-row">
    <!-- Left Section -->
    <div class="relative h-full basis-1/2 bg-red-400">
      <div class="grid grid-rows-[2fr_2fr] h-full">
        <!-- First Section: 50% -->
        <div class="row-span-1 bg-green-400">
          <div class="flex h-full">
            <!-- First 50% of the Green Container -->
            <div class="basis-1/2 bg-green-500 p-4">
              <GlyphOverview :values="values" :height="300" :width="300"></GlyphOverview>
            </div>
            <div class="basis-1/2 bg-green-500 p-4">
              <SDGExplorerLeaderboard></SDGExplorerLeaderboard>
            </div>
          </div>
        </div>

        <!-- Second Section: 50% -->
        <div class="row-span-1 bg-orange-400 flex items-center justify-center">
          <LeaderBoardExplanation></LeaderBoardExplanation>
        </div>
      </div>
    </div>

    <!-- Right Section -->
    <div class="flex h-full basis-1/2 flex-col items-center justify-center bg-blue-400">
      <LeaderBoard></LeaderBoard>
    </div>
  </div>
</template>

<script setup lang="ts">
import SDGExplorerLeaderboard from "~/components/SDGExplorerLeaderboard.vue";
import LeaderBoardExplanation from "~/components/LeaderBoardExplanation.vue";

// Values for the HexGlyph component (example)
const values = Array(17).fill(0.6);

</script>

<style scoped>

</style>
