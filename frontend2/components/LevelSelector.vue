<template>
  <div class="flex flex-col items-center">
    <!-- Title Section -->
    <p class="text-xl font-semibold text-gray-700 mt-4 mb-6">Choose Your Challenge</p>

    <!-- Conditionally Render Description Above the Play Button -->
    <div  class="text-center">
      <p v-if="selectedLevel" class="text-sm text-gray-500">
        {{ getDescriptionForLevel(selectedLevel) }}
      </p>
      <p v-else class="text-sm text-gray-500">
        Select a level from below to get more information.
      </p>
    </div>

    <!-- Levels Container -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 p-4">
      <div
        v-for="level in levels"
        :key="level.id"
        :class="[
          'p-6 rounded-lg text-center cursor-pointer transition-all hover:scale-105',
          level.id === selectedLevel ? 'ring-4 ring-black' : 'border'
        ]"
        @click="selectLevel(level.id)"
      >
        <UIcon
          :name="level.icon"
          class="w-10 h-10 mx-auto"
          :style="{ color: sdgColor }"
        />
      </div>
    </div>

    <!-- Play Button and Leaderboard Toggle -->
    <div class="flex items-center gap-4 mt-6">
      <!-- Show Leaderboard Toggle -->
      <div v-if="currentSDG" class="flex items-center gap-2">
        <label class="inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            v-model="gameStore.showLeaderboard"
            class="sr-only peer"
          />
          <div
            class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-gray-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all"
            :style="{ backgroundColor: gameStore.showLeaderboard ? sdgColor : '#E5E7EB' }"
          ></div>
          <span class="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">
            Show Leaderboard
          </span>
        </label>
      </div>

      <!-- Play Button -->
      <UButton
        @click="play"
        :color="'primary'"
        :variant="'solid'"
        :block="false"
        :disabled="!selectedLevel"
      >
        Play
      </UButton>
    </div>

  </div>
</template>

<script setup>
import { useGameStore } from '@/stores/game';
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useSDGsStore } from "~/stores/sdgs";

// Use the router and store in the setup function
const router = useRouter();
const sdgsStore = useSDGsStore();
const gameStore = useGameStore();
const { sdg } = storeToRefs(gameStore);

// Reactive state for the selected level
const selectedLevel = ref(null);

// Levels data with descriptions and corresponding cellular icons
const levels = [
  { id: 1, tier: 'bronze', description: 'A beginner-friendly challenge to get you started.', icon: 'mdi-signal-cellular-1' },
  { id: 2, tier: 'silver', description: 'For those who seek moderate difficulty.', icon: 'mdi-signal-cellular-2' },
  { id: 3, tier: 'gold', description: 'The ultimate test of your abilities. Only for the brave!', icon: 'mdi-signal-cellular-3' }
];

// Method to select a level
const selectLevel = (levelId) => {
  if (selectedLevel.value === levelId) {
    selectedLevel.value = null;  // Deselect the level
    gameStore.setLevel(null);     // Clear the stored level
  } else {
    selectedLevel.value = levelId;  // Select the level
    gameStore.setLevel(levelId);     // Store the selected level
  }
};

// Method to get description for the selected level
const getDescriptionForLevel = (levelId) => {
  const selected = levels.find(level => level.id === levelId);
  return selected ? selected.description : '';
};

// Method to navigate to the exploration page
const play = () => {
  if (selectedLevel.value && sdg.value) {
    router.push(`/exploration/sdgs/${sdg.value}/${selectedLevel.value}`);
  }
};

// Get the currently selected SDG
const currentSDG = computed(() => {
  const sdgId = gameStore.getSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Computed property to get the color of the selected SDG
const sdgColor = computed(() => {
  return currentSDG.value ? sdgsStore.getColorBySDG(currentSDG.value.id) : "#A0A0A0"; // Default gray if no SDG
});

</script>
