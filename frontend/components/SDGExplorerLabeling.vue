<template>
  <div
    class="flex items-center gap-3 rounded-[var(--radius)] border border-line bg-surface/80 px-3 py-2 shadow-panel backdrop-blur-sm"
    :style="currentSDG ? { boxShadow: `inset 3px 0 0 ${currentSDG.color}` } : {}"
  >
    <template v-if="currentSDG">
      <!-- SDG Icon -->
      <img
        :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
        :alt="`SDG ${currentSDG.id} Icon`"
        class="w-9 h-9 flex-shrink-0 rounded-md"
      >

      <!-- SDG Details (Compact) -->
      <div class="min-w-0 flex-1">
        <p class="font-mono text-[10px] uppercase tracking-wider text-fg-faint">explaining · sdg_{{ String(currentSDG.index).padStart(2, '0') }}</p>
        <p class="truncate text-sm font-semibold text-fg">{{ currentSDG.name }}</p>
      </div>

      <div v-if="machineScore !== null" class="flex-none w-32">
        <div class="flex items-baseline justify-between font-mono text-[10px] text-fg-faint">
          <span>machine score</span><b class="text-xs text-fg">{{ machineScore.toFixed(2) }}</b>
        </div>
        <div class="mt-1 h-1.5 rounded-full bg-muted-strong overflow-hidden">
          <div class="h-full rounded-full transition-[width] duration-500" :style="{ width: `${Math.round(machineScore * 100)}%`, background: currentSDG.color }" />
        </div>
      </div>
    </template>

    <template v-else>
      <!-- Placeholder (Compact) -->
      <div class="flex items-center gap-2.5 text-fg-dim">
        <Icon name="mdi-gesture-tap" class="w-5 h-5 text-accent" />
        <p class="text-sm truncate">Select an SDG above to highlight the machine's reasoning in the abstract</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";

const sdgsStore = useSDGsStore();
const sdgPredictionsStore = useSDGPredictionsStore();

// Get the selected SDG
const currentSDG = computed(() => {
  const sdgId = sdgsStore.getSelectedSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Compute the machine score based on the selected SDG
const machineScore = computed(() => {
  if (!currentSDG.value || !sdgPredictionsStore.labelingSDGPrediction) return null;

  // Extract the score dynamically from the prediction object
  return sdgPredictionsStore.labelingSDGPrediction[`sdg${currentSDG.value.id}`] ?? null;
});

// Fetch SDG Predictions when component mounts
onMounted(async () => {
  if (!sdgPredictionsStore.labelingSDGPrediction) {
    await sdgPredictionsStore.fetchDefaultModelSDGPredictionsByPublicationId(1); // Adjust `1` as needed
  }
});

</script>
