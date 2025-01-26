<template>
  <div class="flex h-full flex-row">
    <!-- Left Section -->
    <div class="relative h-full basis-1/2 bg-red-400">
      <p>SDG-Centered</p>
      <GlyphOverview :values="values" :height="600" :width="600"></GlyphOverview>
    </div>

    <!-- Right Section -->
    <div class="flex h-full basis-1/2 flex-col items-center justify-center bg-blue-400">
      <p class="mb-4 text-xl font-bold text-white">Game Levels (publication-centered)</p>
      <div class="grid grid-cols-3 gap-12">
        <div
          v-for="(level, index) in levels"
          :key="index"
          class="col-span-1 cursor-pointer"
          @click="handleLevelClick(level.level)"
        >
          <div
            :class="`flex flex-col items-center justify-center rounded-md border-4 p-2 ${level.borderClass} relative`"
          >
            <div class="aspect-w-1 aspect-h-1">
              <div :class="`flex items-center justify-center p-4 font-semibold text-white ${level.bgColor}`">
                {{ level.level }}
              </div>
            </div>
            <div class="absolute bottom-2 flex space-x-1">
              <span v-for="star in level.stars" :key="star" class="text-yellow-400">&#9733;</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useGameStore } from "~/stores/game";


const router = useRouter();
const gameStore = useGameStore();

// Values for the HexGlyph component (example)
const values = Array(17).fill(0.6);

// Levels configuration
const levels = [
  { level: 1, bgColor: "bg-gray-400", borderClass: "border-gray-600", stars: 1 },
  { level: 2, bgColor: "bg-gray-500", borderClass: "border-gray-600", stars: 2 },
  { level: 3, bgColor: "bg-gray-600", borderClass: "border-gray-600", stars: 3 },
  { level: 4, bgColor: "bg-slate-400", borderClass: "border-slate-500", stars: 1 },
  { level: 5, bgColor: "bg-slate-500", borderClass: "border-slate-500", stars: 2 },
  { level: 6, bgColor: "bg-slate-600", borderClass: "border-slate-500", stars: 3 },
  { level: 7, bgColor: "bg-yellow-400", borderClass: "border-yellow-600", stars: 1 },
  { level: 8, bgColor: "bg-yellow-500", borderClass: "border-yellow-600", stars: 2 },
  { level: 9, bgColor: "bg-yellow-600", borderClass: "border-yellow-600", stars: 3 },
];

// Handle level click
const handleLevelClick = (level: number) => {
  gameStore.setLevel(level); // Update the current level in the store
  router.push(`/exploration/publications/${level}`); // Redirect to the corresponding route
};
</script>

<style scoped>
/* Ensure aspect ratio is 1:1 for squareness */
.aspect-w-1 {
  aspect-ratio: 1;
}

.aspect-h-1 {
  aspect-ratio: 1;
}
</style>
