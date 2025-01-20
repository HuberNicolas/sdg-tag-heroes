<template>
  <div class="flex flex-row h-full">
    <div class="basis-1/2 h-full bg-red-400 relative">
      <p>SDG-Centered</p>
      <HexGlyph :values="values" :height="600" :width="600" />
    </div>
    <div class="basis-1/2 h-full bg-blue-400 flex flex-col items-center justify-center">
      <p class="text-white font-bold text-xl mb-4">Game Levels (publication-centered)</p>
      <div class="grid grid-cols-3 gap-12">
        <div v-for="(level, index) in levels" :key="index" class="col-span-1">
          <div :class="`p-2 rounded-md border-4 ${level.borderClass} flex flex-col items-center justify-center relative`">
            <div class="aspect-w-1 aspect-h-1">
              <div :class="`flex items-center justify-center text-white font-semibold p-4 ${level.bgColor}`">
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
import HexGlyph from "~/components/GlyphOverview.vue";

// Values for the HexGlyph component (example)
const values = Array(17).fill(0.6);

// Levels configuration
const levels = [
  { level: 1, bgColor: 'bg-gray-400', borderClass: 'border-gray-600', stars: 1 },
  { level: 2, bgColor: 'bg-gray-500', borderClass: 'border-gray-600', stars: 2 },
  { level: 3, bgColor: 'bg-gray-600', borderClass: 'border-gray-600', stars: 3 },
  { level: 4, bgColor: 'bg-slate-400', borderClass: 'border-slate-500', stars: 1 },
  { level: 5, bgColor: 'bg-slate-500', borderClass: 'border-slate-500', stars: 2 },
  { level: 6, bgColor: 'bg-slate-600', borderClass: 'border-slate-500', stars: 3 },
  { level: 7, bgColor: 'bg-yellow-400', borderClass: 'border-yellow-600', stars: 1 },
  { level: 8, bgColor: 'bg-yellow-500', borderClass: 'border-yellow-600', stars: 2 },
  { level: 9, bgColor: 'bg-yellow-600', borderClass: 'border-yellow-600', stars: 3 }
];
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
