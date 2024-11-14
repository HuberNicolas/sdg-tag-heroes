<template>
  <div class="publications-container">
    <div id="scatter-plot-webgl">
      <d3fc-canvas use-device-pixel-ratio set-webgl-viewport/>
    </div>
    <div id="scatter-plot"/>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import UsePublication from '~/composables/usePublication';
import useScatterPlotWebGL from "~/composables/useScatterPlotWebGL";
import useScatterPlot from "~/composables/useScatterPlot";

useScatterPlotWebGL();
useScatterPlot();

const publications = ref<any[]>([]);
const loading = ref<boolean>(false);
const error = ref<string | null>(null);

// Pagination State
const currentPage = ref<number>(1);
const totalPages = ref<number>(0);
const hasMorePages = ref<boolean>(false);

const fetchPublications = async (page = 1) => {
  loading.value = true;
  error.value = null;

  try {
    const publicationService = new UsePublication();
    const response = await publicationService.getPublications(['dimred'], page);

    if (page === 1) {
      publications.value = response.items; // Reset publications on form submit
    } else {
      publications.value = [...publications.value, ...response.items]; // Append results on "Load More"
    }

    currentPage.value = response.page;
    totalPages.value = response.pages;
    hasMorePages.value = currentPage.value < totalPages.value;
  } catch (err: any) {
    error.value = err.message || 'Failed to fetch publications';
  } finally {
    loading.value = false;
  }
};




onMounted(() => {
  fetchPublications();
});
</script>

<style scoped>
.publications-container {

  width: 100%;
  height: 800px;
}
d3fc-canvas {
  width: 100%;
  height: 100%;
}
#scatter-plot-webgl {
  background-color: red;
  width: 100%;
  height: 50%;
}
#scatter-plot {
  background-color: blue;
  width: 100%;
  height: 50%;
}

</style>
