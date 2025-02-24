<template>
  <div class="frame-container">
    <div class="frame-title"><b>Legend</b></div>
    <div class="flex flex-col gap-2 p-3 bg-gray-100 rounded-lg">
      <!-- First Group with Title -->
      <div class="flex gap-3">
        <p class="text-xs font-bold text-gray-700 rotate-180 writing-mode-vertical-rl">Publications</p>
        <div class="flex flex-col gap-2">
          <div v-for="(item, index) in firstGroup" :key="'group1-' + index" class="flex items-center gap-2">
            <p class="text-xs text-gray-700 w-24 text-right">{{ item.description }}</p>
            <UTooltip :text="item.tooltip" :popper="{ strategy: 'absolute', placement: 'top', arrow: true }">
              <figure>
                <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
              </figure>
            </UTooltip>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <hr class="w-full border-t border-gray-400 my-1" />

      <!-- Second Group with Title -->
      <div class="flex gap-3">
        <p class="text-xs font-bold text-gray-700 rotate-180 writing-mode-vertical-rl">Quest Publications</p>
        <div class="flex flex-col gap-2">
          <div v-for="(item, index) in secondGroup" :key="'group2-' + index" class="flex items-center gap-2">
            <p class="text-xs text-gray-700 w-24 text-right">{{ item.description }}</p>
            <UTooltip :text="item.tooltip" :popper="{ strategy: 'absolute', placement: 'top', arrow: true }">
              <figure>
                <img :src="item.src" :alt="item.alt" class="w-14 h-14 object-contain" :style="computedStyle(item.scale)" />
              </figure>
            </UTooltip>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <hr class="w-full border-t border-gray-400 my-1" />

      <!-- Special Last Entry -->
      <div class="flex items-center justify-center gap-1">
        <p class="text-xs text-gray-700 w-24 text-right">Point of Interest</p>
        <UTooltip text="This marks a specific point of interest in the plot." :popper="{ strategy: 'absolute', placement: 'top', arrow: true }">
          <figure class="text-2xl">📍</figure>
        </UTooltip>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const firstGroup = ref([
  {
    src: '/img/case3.png',
    alt: 'Case 3',
    description: 'Low XP',
    tooltip: 'A standard publication (Hexagon) with low XP (Size). The border color represents the highest AI-predicted SDG, indicating its strongest classification.',
    scale: 0.5
  },
]);

const secondGroup = ref([
  {
    src: '/img/case2.png',
    alt: 'Case 2',
    description: 'High XP',
    tooltip: 'A Quest Publication (Diamond) with high XP (Size). The border color represents the highest AI-predicted SDG, highlighting its most confident classification.',
    scale: 1.2
  },
]);


const computedStyle = (scale) => ({
  transform: `scale(${scale})`,
  transition: 'transform 0.2s ease-in-out',
});
</script>

<style scoped>
/* Vertical text styling */
.writing-mode-vertical-rl {
  writing-mode: vertical-rl;
  text-orientation: mixed;
}
</style>
