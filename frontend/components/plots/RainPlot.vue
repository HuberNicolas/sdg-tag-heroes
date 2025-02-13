<template>
  <div class="flex flex-col items-center justify-center bg-gray-100 p-4 rounded-lg shadow-md w-full">
    <!-- D3 Raincloud Plot -->
    <div ref="chartContainer" class="w-full h-40 relative" ></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";
import { useSDGPredictionsStore } from "@/stores/sdgPredictions";
import { calculateEntropy } from "@/utils/entropy";

export default {
  setup() {
    const sdgPredictionsStore = useSDGPredictionsStore();
    const chartContainer = ref(null);

    // Compute entropy values from predictions
    const entropyData = computed(() => {
      return sdgPredictionsStore.selectedPartitionedSDGPredictions.map(prediction => calculateEntropy(prediction));
    });

    // Function to update the Raincloud Plot
    const updateChart = () => {
      if (!chartContainer.value) return;

      const data = entropyData.value;
      const width = chartContainer.value.clientWidth;
      const height = 120;
      const margin = { top: 5, right: 5, bottom: 50, left: 40 };

      if (!data || data.length === 0) {
        d3.select(chartContainer.value).select("svg").remove();
        return;
      }

      // Remove existing SVG if present
      d3.select(chartContainer.value).select("svg").remove();

      const svg = d3.select(chartContainer.value)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Sort data for boxplot
      const sortedData = data.sort(d3.ascending);
      const q1 = d3.quantile(sortedData, 0.25) ?? 0;
      const median = d3.quantile(sortedData, 0.5) ?? 0;
      const q3 = d3.quantile(sortedData, 0.75) ?? 0;
      const iqr = q3 - q1;
      const min = Math.max(d3.min(sortedData) ?? 0, q1 - 1.5 * iqr);
      const max = Math.min(d3.max(sortedData) ?? 0, q3 + 1.5 * iqr);

      // Define scales
      const xScale = d3.scaleLinear().domain([min, max]).range([0, width - margin.left - margin.right]);

      // Tooltip
      const tooltip = d3.select(chartContainer.value)
        .append("div")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "white")
        .style("border", "1px solid black")
        .style("padding", "5px")
        .style("border-radius", "5px")
        .style("opacity", 0)
        .style("pointer-events", "none");

      // Density Curve
      const histogram = d3.bin().thresholds(20)(sortedData).map(bin => bin.length);
      const xScaleHist = d3.scaleLinear().domain([0, histogram.length]).range([0, width - margin.left - margin.right]);
      const yScaleHist = d3.scaleLinear().domain([0, d3.max(histogram)]).range([40, 0]);

      const area = d3.area()
        .x((_, i) => xScaleHist(i))
        .y0(yScaleHist(0))
        .y1(d => yScaleHist(d))
        .curve(d3.curveBasis);

      svg.append("path")
        .datum(histogram)
        .attr("d", area)
        .style("fill", "grey")
        .style("opacity", 0.6);

      // Boxplot
      const boxHeight = 8;
      const yBoxplot = height * 0.5;

      svg.append("line").attr("x1", xScale(min)).attr("x2", xScale(max)).attr("y1", yBoxplot).attr("y2", yBoxplot).attr("stroke", "black");
      svg.append("rect").attr("x", xScale(q1)).attr("y", yBoxplot - boxHeight / 2)
        .attr("width", xScale(q3) - xScale(q1)).attr("height", boxHeight)
        .attr("fill", "grey").attr("opacity", 0.6);
      svg.append("line").attr("x1", xScale(median)).attr("x2", xScale(median)).attr("y1", yBoxplot - boxHeight / 2).attr("y2", yBoxplot + boxHeight / 2).attr("stroke", "black");

      // Dots with tooltip
      const jitterHeight = 30;
      svg.selectAll("circle")
        .data(sortedData)
        .enter()
        .append("circle")
        .attr("r", 5)
        .attr("cx", d => xScale(d))
        .attr("cy", () => height * 0.75 + (Math.random() - 0.5) * jitterHeight)
        .style("fill", "grey")
        .style("opacity", 0.6)
        .on("mouseover", function(event, d) {
          tooltip.style("visibility", "visible").html(`Value: ${d.toFixed(2)}`)
            .style("left", `${event.pageX + 10}px`).style("top", `${event.pageY}px`);
          d3.select(this).attr("stroke", "black").attr("stroke-width", 1);
        })
        .on("mouseout", function() {
          tooltip.style("visibility", "hidden");
          d3.select(this).attr("stroke", "none");
        });

      // X-Axis with rotated labels
      svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(xScale).tickSize(0))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-0.8em")
        .attr("dy", "0.15em")
        .attr("transform", "rotate(-45)");
    };

    // Watch for updates in data
    watch(() => sdgPredictionsStore.selectedPartitionedSDGPredictions, updateChart, { deep: true });

    // Initialize chart
    onMounted(() => {
      updateChart();
    });

    return {
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
