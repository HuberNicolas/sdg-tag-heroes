<template>
  <div class="frame-container flex flex-col gap-2">
    <div class="flex-none flex flex-wrap items-center justify-between gap-2">
      <div class="frame-title !mb-0"><b>Explore</b> Publications on the <b>Publication Map</b>: lasso, hover and click to discover patterns</div>
      <MapHudBadge :label="`sdg_${String(gameStore.getSDG ?? '?').padStart(2, '0')} · level_${gameStore.getLevel ?? '?'}`" :color="sdgColor" :busy="ready && isBusy" />
    </div>

    <div class="relative flex-1 min-h-0">
      <div ref="scatterPlotContainer" class="absolute inset-0" />
      <Transition name="fade">
        <LoadingState v-if="!ready" overlay label="loading publication map" />
      </Transition>
    </div>

    <MapLegend class="flex-none" variant="sdg" :sdg-color="sdgColor" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { createScatterSDGPlot } from '@/composables/plots/scatterSDGPlot';
import { useGameStore } from "~/stores/game";
import { useSDGsStore } from "~/stores/sdgs";

const gameStore = useGameStore();
const sdgsStore = useSDGsStore();
const { isBusy } = useApiActivity();
const scatterPlotContainer = ref<HTMLDivElement | null>(null);
const ready = ref(false);
const sdgColor = computed(() => (gameStore.getSDG ? sdgsStore.getColorBySDG(gameStore.getSDG) : undefined) || '#888888');

onMounted(() => {
  if (scatterPlotContainer.value) {
    scatterPlotContainer.value.addEventListener('hexmap:ready', () => (ready.value = true), { once: true });
    createScatterSDGPlot(scatterPlotContainer.value);
  }
});
</script>

<style scoped>
.fade-leave-active {
  transition: opacity 0.35s;
}
.fade-leave-to {
  opacity: 0;
}
</style>
