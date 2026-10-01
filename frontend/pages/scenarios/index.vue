<template>
  <div class="min-h-full flex flex-col">
    <!-- Title: the two sub-headings line up with the two columns below -->
    <header class="flex-none border-b border-line px-4 py-5 text-center">
      <p class="kicker">// choose your game mode</p>
      <h1 class="mt-2 text-xl lg:text-2xl 2xl:text-3xl font-bold tracking-tight">
        Help label research publications with the SDGs
      </h1>
      <div class="mt-3 grid grid-cols-1 xl:grid-cols-[1fr_auto_1fr] items-center gap-x-4 gap-y-1 text-base 2xl:text-lg text-fg-dim">
        <p>by choosing an <b class="text-fg">SDG world</b>: one goal, all its publications</p>
        <p class="rounded-full border border-line px-3 py-0.5 font-mono text-xs text-fg-faint justify-self-center">OR</p>
        <p>by exploring a <b class="text-fg">universe</b>: publications of all goals on one map</p>
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
            <div class="frame-title"><b>Ask</b> for a suggestion: describe your skills or interests and a language model proposes a fitting SDG</div>
            <SDGUserQuery />
          </div>
          <LeaderBoardExplanation v-else />
        </div>
      </section>

      <!-- Right: universes (or the leaderboard) -->
      <section class="flex items-center justify-center p-4 xl:p-6 border-t xl:border-t-0 xl:border-l border-line min-h-0">
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
