<template>
  <div class="map-container">
    <div class="top-row">
      <div id="scatter-plot-top-control" class="grid-item"></div>
      <div id="scatter-plot-minimap" class="grid-item"></div>
    </div>
    <div class="bottom-row">
      <div id="scatter-plot" class="grid-item"></div>
      <div id="scatter-plot-bottom-control" class="grid-item">
        <div id="scatter-plot-visible-points"></div>
        <div id="scatter-plot-selected-point"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import useScatterPlotMinimap from "~/composables/useScatterPlotMinimap";
useScatterPlotMinimap();

onMounted(() => {});
</script>

<style scoped>
.map-container {
  display: grid;
  grid-template-rows: auto auto; /* Two rows */
  gap: 5px; /* Adjust spacing between rows */
}

.top-row,
.bottom-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 5px; /* Adjust spacing between columns */
}

.grid-item {
  width: 100%;
  height: 100%;
}

#scatter-plot-top-control {
  height: 200px;
}

#scatter-plot-minimap {
  height: 200px;
}

#scatter-plot {
  height: 400px;
}

#scatter-plot-bottom-control {
  height: 400px;
}
</style>
