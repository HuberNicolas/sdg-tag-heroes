<template>
  <div class="frame-container">
    <div class="frame-title"><b>Legend</b></div>
    <div class="flex gap-5 p-3 bg-gray-100 rounded-lg">
      <!-- First Group with Title -->
      <div class="flex flex-col items-center gap-2">
        <p class="text-xs font-bold text-gray-700">Publications</p>
        <div class="flex gap-3">
          <div v-for="(item, index) in firstGroup" :key="'group1-' + index" class="flex flex-col items-center gap-1 relative group">
            <figure>
              <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
            </figure>
            <p class="text-xs text-gray-700 text-center">{{ item.description }}</p>
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
      <div class="flex flex-col items-center gap-2">
        <p class="text-xs font-bold text-gray-700">Quest Publications</p>
        <div class="flex gap-3">
          <div v-for="(item, index) in secondGroup" :key="'group2-' + index" class="flex flex-col items-center gap-1 relative group">
            <figure>
              <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
            </figure>
            <p class="text-xs text-gray-700 text-center">{{ item.description }}</p>
            <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded-lg py-1 px-2">
              {{ item.tooltip }}
              <div class="absolute left-1/2 transform -translate-x-1/2 top-full border-8 border-transparent border-t-gray-800"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-l border-gray-400 h-auto mx-2"></div>

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

const firstGroup = ref([
  {
    src: '/img/case4gs.png',
    alt: 'Case 3',
    description: 'Low XP',
    tooltip: 'A standard publication (Hexagon) with low XP (Size). The color represents the SDG corresponding to the highest Machine Score',
    scale: 0.5
  },
  {
    src: '/img/case4gs.png',
    alt: 'Case 3',
    description: 'High XP',
    tooltip: 'A standard publication (Hexagon) with high XP (Size). The color represents the SDG corresponding to the highest Machine Score',
    scale: 1.0
  },
]);

const secondGroup = ref([
  {
    src: '/img/case2gs.png',
    alt: 'Case 2',
    description: 'Low XP',
    tooltip: 'A Quest Publication (Diamond) with low XP (Size). The color represents the SDG corresponding to the highest Machine Score',
    scale: 0.5
  },
  {
    src: '/img/case2gs.png',
    alt: 'Case 2',
    description: 'High XP',
    tooltip: 'A Quest Publication (Diamond) with high XP (Size). The color represents the SDG corresponding to the highest Machine Score',
    scale: 1.0
  },
]);


const computedStyle = (scale) => ({
  transform: `scale(${scale})`,
  transition: 'transform 0.2s ease-in-out',
});
</script>
