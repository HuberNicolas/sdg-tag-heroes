<template>
  <div class="frame-container flex flex-col gap-2">
    <div class="flex-none flex flex-wrap items-center justify-between gap-2">
      <div class="frame-title !mb-0"><b>Explore</b> Publications on the <b>Publication Map</b>: lasso, hover and click to discover patterns</div>
      <MapHudBadge :label="`universe_0${gameStore.getLevel ?? '?'}`" :busy="ready && isBusy" />
    </div>

    <div class="relative flex-1 min-h-0">
      <div ref="scatterPlotContainer" class="absolute inset-0" />
      <Transition name="fade">
        <LoadingState v-if="!ready" overlay label="loading publication map" />
      </Transition>
    </div>

    <MapLegend class="flex-none" variant="publications" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { createScatterPlot } from '@/composables/plots/scatterPlot';
import { useGameStore } from "~/stores/game";

const gameStore = useGameStore();
const { isBusy } = useApiActivity();
const scatterPlotContainer = ref<HTMLDivElement | null>(null);
const ready = ref(false);
const mapPartitions = Number(useRuntimeConfig().public.mapPartitions) || 1000;

onMounted(() => {
  if (scatterPlotContainer.value) {
    // The map fires this once its first data is drawn
    scatterPlotContainer.value.addEventListener('hexmap:ready', () => (ready.value = true), { once: true });
    createScatterPlot(scatterPlotContainer.value, undefined, undefined, 'top1', mapPartitions);
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
