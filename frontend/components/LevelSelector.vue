<template>
  <div class="flex flex-col items-center">
    <!-- Levels Container -->
    <div class="grid grid-cols-3 gap-4 p-4">
      <div
        v-for="level in levels"
        :key="level.id"
        :class="[
          'p-6 rounded-lg text-center cursor-pointer transition-all',
          level.tier === 'bronze' ? 'bg-orange-200 border-orange-400' : '',
          level.tier === 'silver' ? 'bg-gray-200 border-gray-400' : '',
          level.tier === 'gold' ? 'bg-yellow-200 border-yellow-500' : '',
          level.id === selectedLevel ? 'ring-4 ring-blue-500' : 'border'
        ]"
        @click="selectLevel(level.id)"
      >
        <p class="font-bold text-lg" :class="level.tier === 'gold' ? 'text-yellow-600' : ''">
          {{ level.name }}
        </p>
      </div>
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
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';

// Use the router and store in the setup function
const router = useRouter();
const gameStore = useGameStore();
const { level, sdg } = storeToRefs(gameStore);

// Reactive state for the selected level
const selectedLevel = ref(null);

// Levels data
const levels = [
  { id: 1, name: 'Bronze', tier: 'bronze' },
  { id: 2, name: 'Silver', tier: 'silver' },
  { id: 3, name: 'Gold', tier: 'gold' }
];

// Method to select a level
const selectLevel = (levelId) => {
  selectedLevel.value = levelId;
  gameStore.setLevel(levelId);
};

// Method to navigate to the exploration page
const play = () => {
  if (selectedLevel.value && sdg.value) {
    router.push(`/exploration/sdgs/${sdg.value}/${selectedLevel.value}`);
  }
};
</script>

