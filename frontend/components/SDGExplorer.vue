<template>
  <div class="p-6 space-y-6">
    <!-- SDG Card -->
    <div
      v-if="currentSDG"
      class="sdg-card flex flex-col items-center p-5 rounded-[var(--radius)] border border-line bg-surface/80 backdrop-blur-sm"
      :style="{ '--sdg': sdgColor }"
    >
      <!-- SDG Index and SDG Short Title  -->
      <p class="font-mono text-xs" :style="{ color: sdgColor }">// sdg_{{ String(currentSDG.index).padStart(2, '0') }}</p>
      <h2 class="text-xl font-bold tracking-tight text-fg mb-3">
        SDG {{currentSDG.index}} - {{ currentSDG.shortTitle }}
      </h2>

      <!-- SDG Icon -->
      <img
        :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
        :alt="`SDG ${currentSDG.id} Icon`"
        class="w-20 h-20 mb-4 rounded-xl shadow-panel"
      >

      <!-- Catchy Explanation -->
      <p class="text-center text-fg-dim mt-1 mb-3">
        {{ currentSDG.explanation }}
      </p>

      <!-- Keywords Section -->
      <div v-if="currentSDG" class="flex gap-1 flex-wrap p-1">
        <span
          v-for="(keyword, index) in currentSDG.keywords.split(',')"
          :key="index"
          class="px-2.5 py-0.5 font-mono text-xs rounded-full border"
          :style="{ color: sdgColor, borderColor: sdgColor, backgroundColor: `${sdgColor}1a` }"
        >
          {{ keyword.trim() }}
        </span>
      </div>
      <LevelSelector/>
    </div>
    <div v-else class="flex flex-col items-center gap-3 rounded-[var(--radius)] border border-dashed border-line-strong p-8 text-center">
      <Icon name="mdi-hexagon-multiple-outline" class="h-10 w-10 text-accent" />
      <p class="font-mono text-sm text-fg-dim">
        <span class="text-accent">&gt;</span> Please select an SDG<span class="animate-blink">_</span>
      </p>
      <p class="text-xs text-fg-faint">Click a honeycomb cell to enter its world.</p>
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

<style scoped>
.sdg-card {
  box-shadow: var(--shadow), inset 0 1px 0 0 color-mix(in srgb, var(--sdg) 60%, transparent);
}
</style>
