<template>
  <div class="flex flex-col items-center justify-center bg-gray-100 pt-0 pb-0 pr-4 pl-4 rounded-sm shadow-md w-full">
    <!-- D3 Bar Chart -->
    <p class="text-sm text-gray-600">
      Top SDG-Goal Distribution
    </p>
    <div ref="chartContainer" class="w-full"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";
import { usePublicationsStore } from "@/stores/publications";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useSDGsStore } from "@/stores/sdgs";

export default {
  setup() {
    const publicationsStore = usePublicationsStore();
    const sdgPredictionsStore = useSDGPredictionsStore();
    const sdgsStore = useSDGsStore();
    const chartContainer = ref(null);

    // Reactive values for total publications
    const totalCount = ref(publicationsStore.sdgLevelPublications.length);

    // Function to compute SDG bar chart data
    const computeSDGData = (predictions) => {
      const sdgCounts = Array(17).fill(0); // Array to store SDG counts

      predictions.forEach(prediction => {
        const maxSDG = Object.entries(prediction)
          .filter(([key]) => key.startsWith('sdg'))
          .reduce((max, [key, value]) => (value > max.value ? { key, value } : max), { key: null, value: 0 });

        if (maxSDG.key) {
          const sdgId = parseInt(maxSDG.key.replace("sdg", ""), 10);
          if (sdgId >= 1 && sdgId <= 17) {
            sdgCounts[sdgId - 1]++;
          }
        }
      });

      return sdgCounts.map((count, index) => ({
        sdgId: index + 1,
        count,
        color: sdgsStore.getColorBySDG(index + 1),
      })).filter(d => d.count > 0); // Remove SDGs that are not present
    };

    const sdgDistribution = computed(() => computeSDGData(sdgPredictionsStore.selectedPartitionedSDGPredictions));

    // Function to update the D3 bar chart
    const updateChart = () => {
      if (!chartContainer.value) return;

      const data = sdgDistribution.value;
      const width = chartContainer.value.clientWidth;
      const height = 120;
      const margin = { top: 5, right: 5, bottom: 60, left: 30 }; // Increased left margin for Y-axis

      // Remove existing SVG if present
      d3.select(chartContainer.value).select("svg").remove();

      // Create SVG container
      const svg = d3.select(chartContainer.value)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Define scales
      const xScale = d3.scaleBand()
        .domain(data.map(d => `SDG ${d.sdgId}`))
        .range([0, width - margin.left - margin.right])
        .padding(0.2);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count) || 1])
        .range([height - margin.top - margin.bottom, 0]);

      // Tooltip setup
      const tooltip = d3.select(chartContainer.value)
        .append("div")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "#fff")
        .style("border", "1px solid #ddd")
        .style("padding", "5px")
        .style("border-radius", "4px")
        .style("font-size", "12px")
        .style("box-shadow", "0px 0px 6px rgba(0,0,0,0.2)");

      // Add bars with tooltip behavior
      svg.selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", d => xScale(`SDG ${d.sdgId}`))
        .attr("y", d => yScale(d.count))
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - margin.top - margin.bottom - yScale(d.count))
        .attr("fill", d => d.color)
        .attr("rx", 4)
        .on("mouseover", (event, d) => {
          tooltip.style("visibility", "visible")
            .text(`SDG ${d.sdgId}: ${d.count}`)
            .style("background-color", d.color); // Set the tooltip background color to the SDG's color
        })
        .on("mousemove", (event) => {
          tooltip.style("top", `${event.pageY - 30}px`)
            .style("left", `${event.pageX + 10}px`);
        })
        .on("mouseout", () => {
          tooltip.style("visibility", "hidden");
        });

      // Add X axis with rotated labels
      svg.append("g")
        .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(xScale).tickSize(0))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-0.8em")
        .attr("dy", "0.15em")
        .attr("transform", "rotate(-30)");

      // Add Y axis
      svg.append("g")
        .call(d3.axisLeft(yScale).ticks(4));
    };


    // Watch for changes and update chart
    watch(
      () => publicationsStore.sdgLevelPublications.length,
      (newTotal) => {
        totalCount.value = newTotal;
        updateChart();
      }
    );

    watch(
      () => sdgPredictionsStore.selectedPartitionedSDGPredictions,
      () => {
        updateChart();
      },
      { deep: true }
    );

    // Initialize chart on mount
    onMounted(() => {
      updateChart();
    });

    return {
      totalCount,
      chartContainer,
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
