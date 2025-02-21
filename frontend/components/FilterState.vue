<template>
  <div class="flex flex-col items-center justify-center bg-gray-100 pt-0 pb-0 pr-4 pl-4 rounded-sm shadow-md w-full">
    <!-- Text Information -->
    <p class="text-sm text-gray-600">
      Selected <span class="font-bold" :style="{ color: sdgColor }">{{ selectedCount }}</span> of
      <span class="font-bold text-black-600">{{ totalCount }}</span> publications
    </p>
    <!-- D3 Stacked Bar Chart -->
    <div ref="chartContainer" class="w-full h-1/2"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import * as d3 from "d3";
import { select, scaleLinear } from 'd3';
import { transition } from 'd3-transition';
import { usePublicationsStore } from '@/stores/publications';
import { useSDGPredictionsStore } from '@/stores/sdgPredictions';
import { useGameStore } from '@/stores/game';
import { useSDGsStore } from '@/stores/sdgs';
import {useCollectionsStore} from "@/stores/collections";

// Store hooks
const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const gameStore = useGameStore();
const sdgsStore = useSDGsStore();
const collectionsStore = useCollectionsStore();

// Refs
const chartContainer = ref(null);
const selectedCount = ref(publicationsStore.selectedPartitionedPublications.length);
const totalCount = ref(publicationsStore.sdgLevelPublications.length + publicationsStore.scenarioTypePublications.length);

// Computed properties
const sdgColor = computed(() => {
  const sdgId = gameStore.getSDG;
  return sdgsStore.getColorBySDG(sdgId) || '#464a50';
});

const computeSDGStackedData = (predictions) => {
  const sdgCounts = Array(17).fill(0); // Array to store highest SDG counts

  predictions.forEach(prediction => {
    const sdgValues = [
      { id: 1, value: prediction.sdg1 },
      { id: 2, value: prediction.sdg2 },
      { id: 3, value: prediction.sdg3 },
      { id: 4, value: prediction.sdg4 },
      { id: 5, value: prediction.sdg5 },
      { id: 6, value: prediction.sdg6 },
      { id: 7, value: prediction.sdg7 },
      { id: 8, value: prediction.sdg8 },
      { id: 9, value: prediction.sdg9 },
      { id: 10, value: prediction.sdg10 },
      { id: 11, value: prediction.sdg11 },
      { id: 12, value: prediction.sdg12 },
      { id: 13, value: prediction.sdg13 },
      { id: 14, value: prediction.sdg14 },
      { id: 15, value: prediction.sdg15 },
      { id: 16, value: prediction.sdg16 },
      { id: 17, value: prediction.sdg17 },
    ];

    const highestSDG = sdgValues.reduce((max, sdg) => (sdg.value > max.value ? sdg : max), { id: null, value: 0 });

    if (highestSDG.id !== null) {
      sdgCounts[highestSDG.id - 1]++;
    }
  });

  const total = sdgCounts.reduce((sum, val) => sum + val, 0) || 1;

  return sdgCounts.map((count, index) => ({
    sdgId: index + 1,
    count,
    proportion: count / total,
    color: sdgsStore.getColorBySDG(index + 1),
  })).filter(d => d.count > 0);
};

const selectedSDGDistribution = computed(() =>
  computeSDGStackedData(sdgPredictionsStore.selectedPartitionedSDGPredictions)
);
const trueSDGDistribution = computed(() =>
  computeSDGStackedData(sdgPredictionsStore.scenarioTypeSDGPredictions)
);

const updateChart = () => {
  if (!chartContainer.value) return;

  const selected = selectedCount.value;
  const filteredOut = Math.max(totalCount.value - selected, 0);
  const selectedDistribution = selectedSDGDistribution.value;
  const widthScale = d3.scaleLinear()
    .domain([0, totalCount.value || 1])
    .range([0, 100]);

  // Clear existing SVG and tooltip
  d3.select(chartContainer.value)
    .selectAll('svg')
    .remove();
  d3.select(chartContainer.value)
    .selectAll('.tooltip')
    .remove();

  // Create tooltip
  const tooltip = d3.select(chartContainer.value)
    .append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0);

  // Create SVG
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', '100%')
    .attr('height', '100%');

  // Selected publications bar
  const selectedBar = svg.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('height', '40%')
    .attr('fill', sdgColor.value)
    .attr('width', 0);

  selectedBar
    .on('mouseover', function() {
      tooltip
        .style('opacity', 1)
        .html(`Selected publications: ${selectedCount.value}`)
        .style('background-color', sdgColor.value);
    })
    .on('mousemove', function(event) {
      tooltip
        .style('top', (event.pageY - 30) + 'px')
        .style('left', (event.pageX + 10) + 'px');
    })
    .on('mouseout', function() {
      tooltip.style('opacity', 0);
    })
    .transition()
    .duration(2000)
    .attr('width', widthScale(selected) + '%');

  // Filtered out publications bar
  const filteredBar = svg.append('rect')
    .attr('x', widthScale(selected) + '%')
    .attr('y', 0)
    .attr('height', '40%')
    .attr('fill', '#D1D5DB')
    .attr('width', 0);

  filteredBar
    .on('mouseover', function() {
      tooltip
        .style('opacity', 1)
        .html(`Filtered out publications: ${filteredOut}`)
        .style('background-color', '#D1D5DB');
    })
    .on('mousemove', function(event) {
      tooltip
        .style('top', (event.pageY - 30) + 'px')
        .style('left', (event.pageX + 10) + 'px');
    })
    .on('mouseout', function() {
      tooltip.style('opacity', 0);
    })
    .transition()
    .duration(2000)
    .attr('width', widthScale(filteredOut) + '%');

  // SDG distribution bars
  let xOffset = 0;
  selectedDistribution.forEach(({ proportion, color, sdgId }) => {
    const sdgBar = svg.append('rect')
      .attr('x', xOffset + '%')
      .attr('y', '40%')
      .attr('height', '40%')
      .attr('fill', color)
      .attr('width', 0);

    sdgBar
      .on('mouseover', function() {
        tooltip
          .style('opacity', 1)
          .html(`SDG ${sdgId}: ${(proportion * 100).toFixed(1)}%`)
          .style('background-color', color);
      })
      .on('mousemove', function(event) {
        tooltip
          .style('top', (event.pageY - 30) + 'px')
          .style('left', (event.pageX + 10) + 'px');
      })
      .on('mouseout', function() {
        tooltip.style('opacity', 0);
      })
      .transition()
      .duration(2000)
      .attr('width', proportion * widthScale(selected) + '%');

    xOffset += proportion * widthScale(selected);
  });
};

// Watchers
watch(
  () => publicationsStore.selectedPartitionedPublications.length,
  (newCount) => {
    selectedCount.value = newCount;
    updateChart();
  }
);

watch(
  () => publicationsStore.sdgLevelPublications.length,
  (newTotal) => {
    totalCount.value = newTotal + publicationsStore.scenarioTypePublications.length;
    updateChart();
  }
);

watch(
  () => publicationsStore.scenarioTypePublications.length,
  (newTotal) => {
    totalCount.value = newTotal + publicationsStore.sdgLevelPublications.length;
    updateChart();
  }
);

watch(
  () => collectionsStore.selectedCollections,
  (newCollections) => {
    // Get all publications that belong to the selected collections
    const selectedCollectionIds = new Set(newCollections.map(c => c.collectionId));

    const filteredPublications = publicationsStore.sdgLevelPublications.filter(pub =>
      selectedCollectionIds.has(pub.collectionId)
    ).length + publicationsStore.scenarioTypePublications.filter(pub =>
      selectedCollectionIds.has(pub.collectionId)
    ).length;

    totalCount.value = filteredPublications;
    selectedCount.value = 0;
    updateChart();
  },
  { deep: true }
);


watch(
  () => gameStore.getSDG,
  () => {
    updateChart();
  }
);

// Lifecycle hooks
onMounted(() => {
  updateChart();
});
</script>

<style scoped>
.w-full {
  width: 100%;
}
.tooltip {
  position: absolute;
  padding: 5px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
  box-shadow: 0px 0px 6px rgba(0,0,0,0.2);
  pointer-events: none;
  z-index: 1000;
}
</style>
