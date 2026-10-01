<template>
  <div class="flex flex-col items-center">
    <!-- Title Section -->
    <p class="kicker mt-5">// difficulty</p>
    <p class="text-lg font-semibold tracking-tight text-fg mt-1 mb-3">Choose a difficulty</p>

    <!-- Conditionally Render Description Above the Play Button -->
    <div  class="text-center">
      <p v-if="selectedLevel" class="text-sm text-fg-dim">
        {{ getDescriptionForLevel(selectedLevel) }}
      </p>
      <p v-else class="text-sm text-fg-dim">
        Select a level from below to get more information.
      </p>
    </div>

    <!-- Levels Container -->
    <div class="grid grid-cols-3 gap-3 p-4">
      <div
        v-for="level in levels"
        :key="level.id"
        :class="[
          'level-tile p-4 rounded-xl text-center cursor-pointer transition-all duration-200 hover:-translate-y-0.5 border',
          level.id === selectedLevel ? 'level-tile--active' : 'border-line bg-surface-2'
        ]"
        :style="level.id === selectedLevel ? { borderColor: sdgColor, boxShadow: `0 0 0 1px ${sdgColor}, 0 10px 30px -12px ${sdgColor}` } : {}"
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
            v-model="gameStore.showLeaderboard"
            type="checkbox"
            class="sr-only peer"
          >
          <div
            class="relative w-11 h-6 bg-muted-strong peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-line-strong rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-surface after:border-line after:border after:rounded-full after:h-5 after:w-5 after:transition-all"
            :style="{ backgroundColor: gameStore.showLeaderboard ? sdgColor : 'rgb(var(--c-muted-strong))' }"
          />
          <span class="ms-3 font-mono text-xs text-fg-dim">
            Show Leaderboard
          </span>
        </label>
      </div>

      <!-- Play Button -->
      <UButton
        :color="'primary'"
        :variant="'solid'"
        :block="false"
        :disabled="!selectedLevel"
        trailing-icon="i-mdi-arrow-right"
        @click="play"
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
  { id: 1, tier: 'bronze', description: 'Publications the model is very confident about. A good place to start.', icon: 'mdi-signal-cellular-1' },
  { id: 2, tier: 'silver', description: 'The model is fairly sure, but not always right.', icon: 'mdi-signal-cellular-2' },
  { id: 3, tier: 'gold', description: 'The model is unsure. These publications need careful reading.', icon: 'mdi-signal-cellular-3' }
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
