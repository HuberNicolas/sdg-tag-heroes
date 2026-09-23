<template>
  <div class="min-h-full flex flex-col">
    <!-- Title: the two sub-headings line up with the two columns below -->
    <header class="flex-none bg-gray-50 border-b border-gray-200 px-4 py-3 text-center">
      <h1 class="text-xl lg:text-2xl 2xl:text-3xl font-bold">
        Wanna be an SDG-Tag Hero? Then help us labeling Publications with SDGs either
      </h1>
      <div class="mt-1 grid grid-cols-1 xl:grid-cols-[1fr_auto_1fr] items-center gap-x-4 text-base 2xl:text-xl">
        <p>by <b>Selecting</b> an SDG World</p>
        <p class="font-bold text-gray-700">OR</p>
        <p>by <b>Exploring</b> Publications from different Universes</p>
      </div>
    </header>

    <div class="flex-1 min-h-0 grid grid-cols-1 xl:grid-cols-2">
      <!-- Left: SDG worlds -->
      <section class="flex flex-col gap-4 p-4 xl:p-6 min-h-0">
        <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 items-center gap-6">
          <div class="flex items-center justify-center">
            <GlyphOverviewScenario :values="values" class="w-full max-w-[min(100%,34rem,42vh)]" />
          </div>
          <div class="flex items-center justify-center">
            <SDGExplorer class="w-full max-w-xl" />
          </div>
        </div>

        <div class="flex-none flex justify-center">
          <div v-if="!gameStore.showLeaderboard" class="frame-container w-full max-w-4xl">
            <div class="frame-title"><b>Share</b> either your Skills or Interests with the intelligent agent to receive a customized SDG suggestion in the <b>SDG Suggestion Box</b></div>
            <SDGUserQuery />
          </div>
          <LeaderBoardExplanation v-else />
        </div>
      </section>

      <!-- Right: universes (or the leaderboard) -->
      <section class="flex items-center justify-center p-4 xl:p-6 border-t-4 xl:border-t-0 xl:border-l-4 border-gray-500 min-h-0">
        <WorldSelector v-if="!gameStore.showLeaderboard" class="w-full" />
        <LeaderBoard v-else class="w-full" />
      </section>
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
