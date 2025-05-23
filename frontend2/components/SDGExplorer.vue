<template>
  <div class="p-6 space-y-6">
    <!-- SDG Card -->
    <div
      v-if="currentSDG"
      class="flex flex-col items-center p-4 border rounded-lg shadow-lg bg-white"
    >
      <!-- SDG Index and SDG Short Title  -->
      <h2 class="text-lg font-bold text-gray-900 mb-1">
        SDG {{currentSDG.index}} - {{ currentSDG.shortTitle }}
      </h2>

      <!-- SDG Icon -->
      <img
        :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
        :alt="`SDG ${currentSDG.id} Icon`"
        class="w-16 h-16 mb-4"
      />

      <!-- Catchy Explanation -->
      <p class="text-center text-gray-700 mt-1 mb-2">
        {{ currentSDG.explanation }}
      </p>

      <!-- Keywords Section -->
      <div v-if="currentSDG" class="flex gap-1 flex-wrap p-1">
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
    <div v-else>
      Please select an SDG
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
