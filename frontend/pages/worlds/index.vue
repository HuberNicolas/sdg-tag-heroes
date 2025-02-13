<template>
  <div class="h-full overflow-hidden">
    <div class="grid grid-rows-10 grid-cols-10 grid-flow-col h-full">

      <!-- Left Section (Takes Half of the Grid) -->
      <div class="row-span-10 col-span-5 grid grid-rows-10">

        <!-- First Section: Top Half -->

        <div class="row-span-5 grid grid-cols-2">
          <div class="col-span-1 p-4 flex items-center justify-center">
            <GlyphOverview :values="values" :height="300" :width="300" />
          </div>
          <div class="col-span-1 p-4 flex items-center justify-center">
            <SDGExplorerLeaderboard />
          </div>
        </div>

        <!-- Second Section: Bottom Half -->
        <div class="row-span-5 items-center justify-center">
          <LeaderBoardExplanation />
        </div>
      </div>

      <!-- Right Section (Takes Half of the Grid) -->
      <div class="row-span-10 col-span-5">
        <LeaderBoard />
      </div>

    </div>
  </div>
</template>




<script setup lang="ts">
import SDGExplorerLeaderboard from "~/components/SDGExplorerLeaderboard.vue";
import LeaderBoardExplanation from "~/components/LeaderBoardExplanation.vue";

// Values for the HexGlyph component
const values = Array(17).fill(0.6);

</script>

<style scoped>

</style>
