<template>
  <div class="frame-container">
    <div class="frame-title"><b>Legend</b></div>
    <div class="flex gap-3 p-1 bg-gray-100 rounded-lg">

      <!-- First Group with Title -->
      <div class="flex flex-col items-center">
        <p class="text-xs font-bold text-gray-700">Publication - Top SDG matches <span :style="{ color: sdgColor }">SDG World</span></p>
        <div class="flex">
          <div v-for="(item, index) in firstGroup" :key="'group1-' + index" class="flex flex-col items-center relative group">
            <figure>
              <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
            </figure>
            <p class="text-xs text-gray-700 text-center">{{  item.description[0] }}</p>
            <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded-lg py-1 px-2">
              {{ item.tooltip }}
              <div class="absolute left-1/2 transform -translate-x-1/2 top-full border-8 border-transparent border-t-gray-800"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-l border-gray-400 h-auto mx-2"></div>

      <!-- Second Group with Title -->
      <div class="flex flex-col items-center">
        <p class="text-xs font-bold text-gray-700">Publication - Top SDG different to <span :style="{ color: sdgColor }">SDG World</span></p>
        <div class="flex">
          <div v-for="(item, index) in secondGroup" :key="'group2-' + index" class="flex flex-col items-center relative group">
            <figure>
              <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
            </figure>
            <p class="text-xs text-gray-700 text-center">{{ item.description[0] }}</p>
            <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded-lg py-1 px-2">
              {{ item.tooltip }}
              <div class="absolute left-1/2 transform -translate-x-1/2 top-full border-8 border-transparent border-t-gray-800"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-l-4 border-gray-600 h-auto mx-2"></div>
      <div class="border-l-4 border-gray-600 h-auto mx-2"></div>

      <!-- First Group with Title -->
      <div class="flex flex-col items-center">
        <p class="text-xs font-bold text-gray-700">Quest Publication - Top SDG matches <span :style="{ color: sdgColor }">SDG World</span></p>
        <div class="flex">
          <div v-for="(item, index) in thirdGroup" :key="'group1-' + index" class="flex flex-col items-center relative group">
            <figure>
              <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
            </figure>
            <p class="text-xs text-gray-700 text-center">{{  item.description[0] }}</p>
            <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded-lg py-1 px-2">
              {{ item.tooltip }}
              <div class="absolute left-1/2 transform -translate-x-1/2 top-full border-8 border-transparent border-t-gray-800"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-l border-gray-400 h-auto mx-2"></div>

      <!-- Second Group with Title -->
      <div class="flex flex-col items-center">
        <p class="text-xs font-bold text-gray-700">Quest Publication - Top SDG different to <span :style="{ color: sdgColor }">SDG World</span></p>
        <div class="flex">
          <div v-for="(item, index) in fourthGroup" :key="'group2-' + index" class="flex flex-col items-center relative group">
            <figure>
              <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
            </figure>
            <p class="text-xs text-gray-700 text-center">{{  item.description[0] }}</p>
            <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded-lg py-1 px-2">
              {{ item.tooltip }}
              <div class="absolute left-1/2 transform -translate-x-1/2 top-full border-8 border-transparent border-t-gray-800"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-l-8 border-gray-600 h-auto mx-2"></div>

      <!-- Special Last Entry -->
      <div class="flex flex-col items-center gap-2 relative group">
        <p class="text-xs text-gray-700 text-center">Point of Interest</p>
        <figure class="text-2xl">📍</figure>
        <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded-lg py-1 px-2">
          This marks a specific point of interest in the plot.
          <div class="absolute left-1/2 transform -translate-x-1/2 top-full border-8 border-transparent border-t-gray-800"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useSDGsStore } from "~/stores/sdgs.js";
import { useGameStore } from "~/stores/game.js";

const firstGroup = ref([
  {
    src: '/img/case4gs.png',
    alt: 'Case 3',
    description: ['Low XP', 'Match'],
    tooltip: 'A publication (Hexagon) with low XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are matching.',
    scale: 0.3
  },
  {
    src: '/img/case4gs.png',
    alt: 'Case 1',
    description: ['High XP', 'Match'],
    tooltip: 'A publication (Hexagon) with high XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are matching.',
    scale: 0.6
  },
]);

const secondGroup = ref([
  {
    src: '/img/case1gs.png',
    alt: 'Case 3',
    description: ['Low XP', 'Mismatch'],
    tooltip: 'A publication (Hexagon) with low XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are different.',
    scale: 0.3
  },
  {
    src: '/img/case1gs.png',
    alt: 'Case 1',
    description: ['High XP', 'Mismatch'],
    tooltip: 'A publication (Hexagon) with high XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are different.',
    scale: 0.6
  },
]);

const thirdGroup = ref([
  {
    src: '/img/case2gs.png',
    alt: 'Case 4',
    description: ['Low XP', 'Match'],
    tooltip: 'A Quest Publication (Diamond) with low XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are matching.',
    scale: 0.3
  },
  {
    src: '/img/case2gs.png',
    alt: 'Case 2',
    description: ['High XP', 'Match'],
    tooltip: 'A Quest Publication (Diamond) with high XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are matching.',
    scale: 0.6
  },
]);

const fourthGroup = ref([
  {
    src: '/img/case3gs.png',
    alt: 'Case 4',
    description: ['Low XP', 'Mismatch'],
    tooltip: 'A Quest Publication (Diamond) with low XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are different.',
    scale: 0.3
  },
  {
    src: '/img/case3gs.png',
    alt: 'Case 2',
    description: ['High XP', 'Mismatch'],
    tooltip: 'A Quest Publication (Diamond) with high XP (Size). The center color represents the color of the current SDG World. The border color represents the SDG corresponding to the highest Machine Score: They are different.',
    scale: 0.6
  },
]);

const sdgsStore = useSDGsStore();
const gameStore = useGameStore();

// Get the currently selected SDG
const currentSDG = computed(() => {
  const sdgId = gameStore.getSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Computed property to get the color of the selected SDG
const sdgColor = computed(() => {
  return currentSDG.value ? sdgsStore.getColorBySDG(currentSDG.value.id) : "#A0A0A0"; // Default gray if no SDG
});

const computedStyle = (scale) => ({
  transform: `scale(${scale})`,
  transition: 'transform 0.2s ease-in-out',
});
</script>
