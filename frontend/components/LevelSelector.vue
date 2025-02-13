<template>
  <div class="flex flex-col items-center">

    <!-- Updated "Select a Difficulty" Section with Improved Tailwind Styling -->
    <p class="text-xl font-semibold text-gray-700 mt-4 mb-6">Choose Your Challenge</p>

    <!-- Levels Container -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 p-4">
      <div
        v-for="level in levels"
        :key="level.id"
        :class="[
          'p-6 rounded-lg text-center cursor-pointer transition-all hover:scale-105',
          level.tier === 'bronze' ? 'bg-orange-200 border-orange-400' : '',
          level.tier === 'silver' ? 'bg-gray-200 border-gray-400' : '',
          level.tier === 'gold' ? 'bg-yellow-200 border-yellow-500' : '',
          level.id === selectedLevel ? 'ring-4 ring-black' : 'border'
        ]"
        @click="selectLevel(level.id)"
      >
        <p class="font-bold text-lg" :class="[
    level.tier === 'bronze' ? 'text-orange-800' : '',
    level.tier === 'silver' ? 'text-gray-700' : '',
    level.tier === 'gold' ? 'text-yellow-800' : ''
]">
          {{ level.name }}
        </p>
      </div>
    </div>

    <!-- Conditionally Render Description Above the Play Button -->
    <div v-if="selectedLevel" class="mt-4 text-center">
      <p class="text-sm text-gray-500">
        {{ getDescriptionForLevel(selectedLevel) }}
      </p>
    </div>

    <!-- Play Button -->
    <button
      v-if="selectedLevel"
      class="mt-4 px-6 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600"
      @click="play"
    >
      Play
    </button>
  </div>
</template>

<script setup>
import { useGameStore } from '@/stores/game';
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { storeToRefs } from 'pinia';

// Use the router and store in the setup function
const router = useRouter();
const gameStore = useGameStore();
const { sdg } = storeToRefs(gameStore);

// Reactive state for the selected level
const selectedLevel = ref(null);

// Levels data with descriptions
const levels = [
  { id: 1, name: 'I', tier: 'bronze', description: 'A beginner-friendly challenge to get you started.' },
  { id: 2, name: 'II', tier: 'silver', description: 'For those who want to test their skills with moderate difficulty.' },
  { id: 3, name: 'III', tier: 'gold', description: 'The ultimate test of your abilities. Only for the brave!' }
];

// Method to select a level
const selectLevel = (levelId) => {
  // Toggle the selection: if already selected, deselect; otherwise, select
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
</script>
