<template>
  <div ref="scatterPlotContainer" class="scatter-plot">
    <!-- Scatter Plot will be rendered here -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import Plotly from 'plotly.js-dist';
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { useCollectionsStore } from "~/stores/collections";
import { useSDGsStore } from "~/stores/sdgs";
import { useGameStore } from "~/stores/game";

const props = defineProps({
  width: {
    type: Number,
    required: true,
  },
  height: {
    type: Number,
    required: true,
  },
});

const scatterPlotContainer = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (scatterPlotContainer.value) {
    createCollectionScatterPlot(scatterPlotContainer.value, props.width, props.height);
  }
});

watch([() => props.width, () => props.height], ([newWidth, newHeight]) => {
  if (scatterPlotContainer.value) {
    createCollectionScatterPlot(scatterPlotContainer.value, newWidth, newHeight);
  }
});

async function createCollectionScatterPlot(container: HTMLElement, width: number, height: number) {
  const dimensionalityReductionsStore = useDimensionalityReductionsStore();
  const publicationsStore = usePublicationsStore();
  const collectionsStore = useCollectionsStore();
  const gameStore = useGameStore();
  const sdgsStore = useSDGsStore();

  const level = gameStore.getLevel;
  const sdg = gameStore.getSDG;

  const reductionShorthand = 'UMAP-15-0.0-2';

  const fetchData = async () => {
    await Promise.all([
      dimensionalityReductionsStore.fetchDimensionalityReductionsBySDGAndLevel(sdg, reductionShorthand, level),
      publicationsStore.fetchPublicationsForDimensionalityReductions(sdg, reductionShorthand, level),
      collectionsStore.fetchCollections(),
      sdgsStore.fetchSDGs()
    ]);
  }


  fetchData().then(() => {
    const dimensionalityReductionsData = dimensionalityReductionsStore.sdgLevelReductions;
    const publicationsData = publicationsStore.sdgLevelPublications;
    const collectionsData = collectionsStore.collections;
    console.log(dimensionalityReductionsData, publicationsData, collectionsData);

    let combinedData = dimensionalityReductionsData.map((reduction, index) => {
      const publication = publicationsData[index];

      // Find the collection corresponding to the publication by matching collectionId
      const correspondingCollection = collectionsData.find(collection => collection.collectionId === publication.collectionId);

      return {
        dimensionalityReduction: reduction,
        publication: publication,
        collection: correspondingCollection
      };
    });

    console.log(combinedData);

    const uniqueCollections = Array.from(new Set(combinedData.map(d => d.collection.shortName)));

    const plotData = uniqueCollections.map(collectionName => {
      const collectionData = combinedData.filter(d => d.collection.shortName === collectionName);
      return {
        x: collectionData.map(d => d.dimensionalityReduction.xCoord),
        y: collectionData.map(d => d.dimensionalityReduction.yCoord),
        mode: 'markers',
        type: 'scatter',
        name: collectionName,
        text: collectionData.map(d => d.publication.title || 'Untitled Publication'),
        marker: {
          size: 10,
          color: `hsl(${collectionData[0].collection.collectionId * 30 % 360}, 70%, 50%)`,
          opacity: 0.8,
        },
      };
    });
    console.log(plotData);
    const layout = {
      title: `Collection-Based Scatter Plot for SDG ${sdg}`,
      width: width,
      height: height,
      xaxis: { title: 'X Coordinate', visible: false },
      yaxis: { title: 'Y Coordinate', visible: false },
      showlegend: true,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
    };

    Plotly.newPlot(container, plotData, layout);
  });


}
</script>

<style scoped>
.scatter-plot {
  width: 100%;
  height: 100%;
}
</style>
