<template>
  <div class="p-6 space-y-6">
    <!-- Keywords Section -->
    <div v-if="currentSDG && Array.isArray(currentSDG.keywords)" class="flex gap-2 flex-wrap">
      <span class="px-2 py-1 text-sm text-white bg-blue-500 rounded-full">
        {{ currentSDG.keywords.join(', ') }}
      </span>
    </div>

    <!-- SDG Card -->
    <div
      v-if="currentSDG"
      class="flex flex-col items-center p-4 border rounded-lg shadow-lg bg-white"
    >
      <!-- SDG Icon -->
      <img
        :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
        :alt="`SDG ${currentSDG.id} Icon`"
        class="w-16 h-16 mb-4"
      />

      <!-- SDG Title -->
      <h2 class="text-lg font-bold text-gray-900">
        {{ currentSDG.title }}
      </h2>

      <!-- SDG Short Title -->
      <p class="text-sm text-gray-600 mt-1">
        {{ currentSDG.shortTitle }}
      </p>

      <!-- Catchy Explanation -->
      <p class="text-center text-gray-700 mt-4">
        {{ currentSDG.explanation }}
      </p>

      <LevelSelector></LevelSelector>
    </div>
    <div v-else>
      No SDG Selected
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import LevelSelector from "~/components/LevelSelector.vue";
import { useGameStore } from "~/stores/game";
import {useSDGsStore} from "~/stores/sdgs";

const gameStore = useGameStore();
const sdgsStore = useSDGsStore();

// Get the selected SDG from the store
const currentSDG = computed(() => {
  return sdgsStore.sdgs.find((sdg) => sdg.id === gameStore.getSDG) || null;
});
</script>
