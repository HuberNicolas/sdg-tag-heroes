<template>
  <div class="grid grid-cols-3 gap-4">

    <div class="col-span-2 row-span-1">
      <div id="scatter-plot"></div>
      <div id="scatter-plot-bottom-control">
        <div id="scatter-plot-visible-points"></div>
        <div id="scatter-plot-selected-point"></div>
      </div>
    </div>

    <div class="col-span-1 row-span-1">
      <div id="scatter-plot-top-control"></div>
      <div id="scatter-plot-minimap"></div>
      <div v-if="isLoading" class="flex justify-center items-center">
        <!-- <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-gray-900"></div> -->
        <IconSDGLoader class="w-36 h-36 animate-spin" :fontControlled="false"></IconSDGLoader>
        Loading summary ...
      </div>
    </div>

    <div class="col-start-1 col-span-3 row-span-1">
      <div id="scatter-plot-summary">
        <h3>Summary</h3>
        <!-- Loading spinner -->
        <div v-if="isLoading" class="flex justify-center items-center">
        </div>
        <!-- Summary content -->
        <div v-else>
          <p v-if="selectedSummary">{{ selectedSummary.summary }}</p>
          <div v-if="selectedSummary" class="flex flex-wrap gap-2 mt-2">
              <span
                v-for="keyword in selectedSummary.keywords"
                key="keyword">
                <UBadge :ui="{ rounded: 'rounded-full' }" size="xs">{{keyword}}</UBadge>
              </span>
          </div>
          <p v-else>No points selected for summary.</p>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import useScatterPlotMinimap from "~/composables/useScatterPlotMinimap";
useScatterPlotMinimap();

import { computed } from "vue";
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import IconSDGLoader from '~/assets/sdg_loader_glyph.svg';


const dimensionalityStore = useDimensionalityReductionsStore();

const selectedSummary = computed(() => dimensionalityStore.selectedSummary);
const isLoading = computed(() => dimensionalityStore.fetching); // Watch fetching state
</script>


<style scoped>

#scatter-plot-minimap {
  height: 200px;
}

#scatter-plot {
  height: 400px;
}

</style>
