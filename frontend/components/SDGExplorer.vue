<template>
  <div class="p-6 space-y-6">
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

      <!-- Keywords Section -->
      <div v-if="currentSDG" class="flex gap-2 flex-wrap p-2">
        <span
          v-for="(keyword, index) in currentSDG.keywords.split(',')"
          :key="index"
          class="px-2 py-1 text-sm text-white rounded-full"
          :style="{ backgroundColor: sdgColor }"
        >
          {{ keyword.trim() }}
        </span>
      </div>
      <LevelSelector></LevelSelector>
    </div>
    <div v-if="currentSDG">
      <label class="inline-flex items-center cursor-pointer">
        <input type="checkbox" v-model="gameStore.showLeaderboard" class="sr-only peer">
        <div
          class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-gray-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all"
          :style="{ backgroundColor: gameStore.showLeaderboard ? sdgColor : '#E5E7EB' }"
        ></div>
        <span class="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">Show Leaderboard</span>
      </label>
    </div>


    <div v-else>
      No SDG Selected
    </div>
  </div>


</template>

<script setup lang="ts">
import { computed } from "vue";
import { useGameStore } from "~/stores/game";
import { useSDGsStore } from "~/stores/sdgs";

const gameStore = useGameStore();
const sdgsStore = useSDGsStore();

// Get the selected SDG from the store
const currentSDG = computed(() => {
  return sdgsStore.sdgs.find((sdg) => sdg.id === gameStore.getSDG) || null;
});

// Computed property to get the color of the selected SDG
const sdgColor = computed(() => {
  return currentSDG.value ? sdgsStore.getColorBySDG(currentSDG.value.id) : "#A0A0A0"; // Default gray if no SDG
});

</script>
