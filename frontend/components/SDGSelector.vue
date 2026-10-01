<template>
  <div class="frame-container">
    <div class="frame-title"><b>Identify & Explore</b> the model's reasoning: pick an SDG to highlight the words behind its score</div>
    <!-- One hexagon chip per SDG; the bar below shows the machine score of this publication -->
    <div class="sdg-chips" :class="{ 'has-selection': !!selectedSDG }" role="radiogroup" aria-label="SDG">
      <button
        v-for="sdg in sdgs"
        :key="sdg.id"
        type="button"
        role="radio"
        :aria-checked="selectedSDG === sdg.id"
        class="sdg-chip"
        :class="{ 'is-selected': selectedSDG === sdg.id }"
        :style="{ '--sdg': sdg.color }"
        :title="`SDG ${sdg.id} · ${sdg.shortTitle}${machineScore(sdg.id) !== null ? ` · machine score ${machineScore(sdg.id)!.toFixed(2)}` : ''}`"
        @click="selectSDG(sdg.id)"
      >
        <span class="sdg-chip__hex hex-clip">{{ sdg.id }}</span>
        <span class="sdg-chip__name">{{ sdg.shortTitle }}</span>
        <span class="sdg-chip__bar"><span :style="{ width: `${Math.round((machineScore(sdg.id) ?? 0) * 100)}%` }" /></span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { baseSdgShortTitles } from "~/constants/sdgs";

const sdgsStore = useSDGsStore();
const selectedSDG = computed(() => sdgsStore.getSelectedSDG);
const sdgPredictionsStore = useSDGPredictionsStore();

// Machine score of this publication for an SDG (0–1), shown as a small bar under the chip
const machineScore = (sdgId: number): number | null => {
  const prediction = sdgPredictionsStore.labelingSDGPrediction as Record<string, number> | null;
  const value = prediction?.[`sdg${sdgId}`];
  return typeof value === "number" ? value : null;
};

// Fetch SDGs on mount
onMounted(async () => {
  if (!sdgsStore.sdgs.length) {
    await sdgsStore.fetchSDGs();
  }
});

const sdgs = computed(() =>
  sdgsStore.sdgs.map((sdg, index) => ({
    id: sdg.id,
    color: sdg.color,
    shortTitle: baseSdgShortTitles[index],
    icon: sdg.icon,
  }))
);

const selectSDG = (sdgId: number) => {
  if (selectedSDG.value === sdgId) {
    // Deselect if already selected
    sdgsStore.setSelectedSDG(0); // Assuming 0 means no selection
  } else {
    // Select the SDG
    sdgsStore.setSelectedSDG(sdgId);
  }
};
</script>

<style scoped>
.sdg-chips {
  @apply grid grid-cols-[repeat(auto-fill,minmax(4rem,1fr))] gap-1.5;
}
.sdg-chip {
  @apply flex flex-col items-center gap-1 rounded-lg border border-transparent px-1 pb-1.5 pt-1 transition-all duration-200;
}
.sdg-chip:hover {
  @apply border-line bg-muted/60;
}
.has-selection .sdg-chip:not(.is-selected) {
  @apply opacity-45 hover:opacity-100;
}
.sdg-chip.is-selected {
  border-color: var(--sdg);
  background: color-mix(in srgb, var(--sdg) 14%, transparent);
  box-shadow: 0 6px 18px -10px var(--sdg);
}
.sdg-chip__hex {
  @apply grid h-8 w-9 place-items-center font-mono text-xs font-bold text-white;
  background: var(--sdg);
}
.sdg-chip__name {
  @apply w-full truncate text-center text-[11.5px] leading-tight text-fg-dim;
}
.sdg-chip.is-selected .sdg-chip__name {
  @apply font-semibold text-fg;
}
.sdg-chip__bar {
  @apply block h-1 w-full overflow-hidden rounded-full bg-muted-strong;
}
.sdg-chip__bar span {
  @apply block h-full rounded-full transition-[width] duration-500;
  background: var(--sdg);
}
</style>
