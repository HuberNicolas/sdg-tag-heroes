<template>
  <div class="map-container">
    <div id="scatter-plot" style="width: 400px; height: 400px;"/>
    <div id="scatter-plot-minimap" style="width: 400px; height: 400px;"/>
  </div>
</template>

<script setup lang="ts">
import useScatterPlotMinimap from "~/composables/useScatterPlotMinimap";
useScatterPlotMinimap();


onMounted(() => {
});
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 800px;
}

#scatter-plot {
  background-color: blue;
  width: 100%;
}
#scatter-plot-minimap {
  background-color: white;
}

</style>
