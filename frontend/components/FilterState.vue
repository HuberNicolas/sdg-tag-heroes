<template>
  <div class="flex flex-col items-center justify-center bg-gray-100 p-4 rounded-lg shadow-md w-full">
    <!-- D3 Stacked Bar Chart -->
    <div ref="chartContainer" class="w-full h-8"></div>

    <!-- Text Information -->
    <p class="text-sm text-gray-600 mt-2">
      Selected <span class="font-bold" :style="{ color: sdgColor }">{{ selectedCount }}</span> of
      <span class="font-bold text-black-600">{{ totalCount }}</span> publications
    </p>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import { select } from "d3-selection";
import { scaleLinear } from "d3-scale";
import { transition } from "d3-transition";
import { usePublicationsStore } from "@/stores/publications";
import { useGameStore } from "@/stores/game";
import { useSDGsStore } from "@/stores/sdgs";

export default {
  setup() {
    const publicationsStore = usePublicationsStore();
    const gameStore = useGameStore();
    const sdgsStore = useSDGsStore();
    const chartContainer = ref(null);

    // Reactive values for selected and total publications
    const selectedCount = ref(publicationsStore.selectedPartitionedPublications.length);
    const totalCount = ref(publicationsStore.sdgLevelPublications.length);

    // Get the SDG color dynamically
    const sdgColor = computed(() => {
      const sdgId = gameStore.getSDG;
      return sdgsStore.getColorBySDG(sdgId) || "#3B82F6"; // Default Blue if SDG color is not found
    });

    // Function to update the D3 stacked bar chart
    const updateChart = () => {
      if (!chartContainer.value) return;

      // Compute counts
      const selected = selectedCount.value;
      const filteredOut = Math.max(totalCount.value - selected, 0);

      // Scale: Converts publication count into a width percentage
      const widthScale = scaleLinear()
        .domain([0, totalCount.value || 1]) // Prevent division by zero
        .range([0, 100]);

      // Select the SVG container
      const svg = select(chartContainer.value)
        .html("") // Clear previous content
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%");

      // Draw the Selected Publications (Uses SDG Color)
      svg.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("height", "100%")
        .attr("rx", 6)
        .attr("ry", 6)
        .attr("fill", sdgColor.value) // Use SDG Color
        .transition(transition().duration(500))
        .attr("width", widthScale(selected) + "%");

      // Draw the Filtered-Out Publications (Gray)
      svg.append("rect")
        .attr("x", widthScale(selected) + "%") // Start where SDG bar ends
        .attr("y", 0)
        .attr("height", "100%")
        .attr("rx", 6)
        .attr("ry", 6)
        .attr("fill", "#D1D5DB") // Gray
        .transition(transition().duration(500))
        .attr("width", widthScale(filteredOut) + "%");
    };

    // Watch for changes in selected publications and update chart
    watch(
      () => publicationsStore.selectedPartitionedPublications.length,
      (newCount) => {
        selectedCount.value = newCount;
        updateChart();
      }
    );

    // Watch for changes in total publications and update chart
    watch(
      () => publicationsStore.sdgLevelPublications.length,
      (newTotal) => {
        totalCount.value = newTotal;
        updateChart();
      }
    );

    // Watch for SDG color change
    watch(
      () => gameStore.getSDG,
      () => {
        updateChart();
      }
    );

    // Initialize the chart when mounted
    onMounted(() => {
      updateChart();
    });

    return {
      selectedCount,
      totalCount,
      chartContainer,
      sdgColor,
    };
  },
};
</script>

<style scoped>
/* Ensure full width */
.w-full {
  width: 100%;
}
</style>
