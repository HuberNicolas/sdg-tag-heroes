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

<script>
import { ref, onMounted, watch, computed } from "vue";
import { select } from "d3-selection";
import { scaleLinear, scaleOrdinal } from "d3-scale";
import { max } from "d3-array";
import { transition } from "d3-transition";
import { usePublicationsStore } from "@/stores/publications";
import { useSDGPredictionsStore} from "~/stores/sdgPredictions.js";
import { useGameStore } from "@/stores/game";
import { useSDGsStore } from "@/stores/sdgs";


export default {
  setup() {
    const publicationsStore = usePublicationsStore();
    const sdgPredictionsStore = useSDGPredictionsStore();

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


    const computeSDGStackedData = (predictions) => {
      const sdgCounts = Array(17).fill(0); // Array to store highest SDG counts

      predictions.forEach(prediction => {
        // Extract all SDG scores and find the highest one
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

        // Find the SDG with the highest score
        const highestSDG = sdgValues.reduce((max, sdg) => (sdg.value > max.value ? sdg : max), { id: null, value: 0 });

        if (highestSDG.id !== null) {
          sdgCounts[highestSDG.id - 1]++; // Increase the count for the highest SDG
        }
      });

      // Calculate total occurrences
      const total = sdgCounts.reduce((sum, val) => sum + val, 0) || 1;

      // Format for stacked bar chart
      return sdgCounts.map((count, index) => ({
        sdgId: index + 1,
        count,
        proportion: count / total, // Convert to percentage width
        color: sdgsStore.getColorBySDG(index + 1),
      })).filter(d => d.count > 0); // Remove SDGs that are not present
    };

// Compute separate distributions
    const selectedSDGDistribution = computed(() =>
      computeSDGStackedData(sdgPredictionsStore.selectedPartitionedSDGPredictions)
    );
    const trueSDGDistribution = computed(() =>
      computeSDGStackedData(sdgPredictionsStore.scenarioTypeSDGPredictions)
    );





    // Function to update the D3 stacked bar chart
    const updateChart = () => {
      if (!chartContainer.value) return;

      // Compute counts
      const selected = selectedCount.value;
      const filteredOut = Math.max(totalCount.value - selected, 0);

      // Compute distributions
      const selectedDistribution = selectedSDGDistribution.value;
      const trueDistribution = trueSDGDistribution.value;

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
        .attr("height", "40%") // Set height of the first bar
        //.attr("rx", 6)
        //.attr("ry", 6)
        .attr("fill", sdgColor.value) // Use SDG Color
        .transition(transition().duration(500))
        .attr("width", widthScale(selected) + "%");

      // Draw the Filtered-Out Publications (Gray)
      svg.append("rect")
        .attr("x", widthScale(selected) + "%") // Start where SDG bar ends
        .attr("y", 0)
        .attr("height", "40%") // Same height as first bar
        //.attr("rx", 6)
        //.attr("ry", 6)
        .attr("fill", "#D1D5DB") // Gray
        .transition(transition().duration(500))
        .attr("width", widthScale(filteredOut) + "%");

      // 🔹 2nd Bar: Stacked SDG Distribution (Selected Publications)
      let xOffset = 0; // Start stacking from 0%

      selectedDistribution.forEach(({ proportion, color }) => {
        svg.append("rect")
          .attr("x", xOffset + "%")
          .attr("y", "40%") // Move below the first bar with some space
          .attr("height", "40%") // Same height as first bar
          //.attr("rx", 6)
          //.attr("ry", 6)
          .attr("fill", color) // Use correct SDG color
          .transition(transition().duration(500))
          .attr("width", proportion * widthScale(selected) + "%"); // Scale width based on selected count

        xOffset += proportion * widthScale(selected); // Move xOffset forward for stacking
      });
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
