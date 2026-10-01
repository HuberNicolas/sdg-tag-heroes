<template>
  <div class="summary-tile">
    <div class="summary-tile__head">
      <span class="summary-tile__key">top SDG per publication</span>
      <button
        v-if="topSdgFilter"
        type="button"
        class="inline-flex items-center gap-1 rounded-full border border-accent/50 bg-accent/10 px-2 py-0.5 font-mono text-[11px] text-fg hover:bg-accent/20"
        title="Show all SDGs in the table"
        @click="clearTopSdgFilter"
      >
        table: SDG {{ topSdgFilter }} <span aria-hidden="true">✕</span>
      </button>
      <span v-else class="summary-tile__meta">click a bar to filter the table</span>
    </div>
    <!-- D3 Bar Chart -->
    <div ref="chartContainer" class="relative w-full"/>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";
import { usePublicationsStore } from "@/stores/publications";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useSDGsStore } from "@/stores/sdgs";
import { baseSdgTitles } from "@/constants/constants";
const sdgTitles = baseSdgTitles

export default {
  setup() {
    const publicationsStore = usePublicationsStore();
    const sdgPredictionsStore = useSDGPredictionsStore();
    const sdgsStore = useSDGsStore();
    const chartContainer = ref(null);
    const { topSdgFilter, toggleTopSdgFilter, clearTopSdgFilter } = useTopSdgFilter();

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
      const height = 96;
      const margin = { top: 14, right: 2, bottom: 18, left: 2 }; // counts on the bars, SDG numbers below

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

      // Tooltip setup (one per chart)
      d3.select(chartContainer.value).selectAll(".glyph-tooltip").remove();
      const tooltip = d3.select(chartContainer.value)
        .append("div")
        .attr("class", "glyph-tooltip")
        .style("position", "absolute")
        .style("z-index", "20")
        .style("pointer-events", "none")
        .style("color", "#fff")
        .style("visibility", "hidden")
        .style("background", "rgb(var(--c-surface))")
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
        .attr("rx", 3)
        .style("cursor", "pointer")
        // With a filter, the other bars step back
        .attr("opacity", d => (topSdgFilter.value && topSdgFilter.value !== d.sdgId ? 0.3 : 1))
        .on("click", (event, d) => toggleTopSdgFilter(d.sdgId))
        .on("mouseover", (event, d) => {
          tooltip.style("visibility", "visible")
            .html(`SDG ${d.sdgId} <br><strong>${sdgTitles[d.sdgId-1]}</strong>: ${d.count} Publications`)
            .style("background-color", d.color); // Set the tooltip background color to the SDG's color
        })
        .on("mousemove", (event) => {
          tooltip.style("top", `${event.pageY - 30}px`)
            .style("left", `${event.pageX + 10}px`);
        })
        .on("mouseout", () => {
          tooltip.style("visibility", "hidden");
        });

      // Count on top of each bar instead of a y axis
      svg.selectAll("text.bar-count")
        .data(data)
        .join("text")
        .attr("class", "bar-count")
        .attr("x", d => xScale(`SDG ${d.sdgId}`) + xScale.bandwidth() / 2)
        .attr("y", d => yScale(d.count) - 3)
        .attr("text-anchor", "middle")
        .style("font", "600 10.5px var(--font-mono)")
        .style("fill", "rgb(var(--c-fg))")
        .text(d => d.count);

      // SDG numbers below the bars (the tooltip has the names)
      const xAxis = svg.append("g")
        .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(xScale).tickSize(0).tickPadding(5).tickFormat(label => label.replace("SDG ", "")));
      xAxis.select(".domain").remove();
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
        // A new selection starts without a table filter
        clearTopSdgFilter();
        updateChart();
      },
      { deep: true }
    );

    watch(topSdgFilter, updateChart);

    // Initialize chart on mount
    // Redraw when the container changes size (window resize, layout changes)
    useRedrawOnResize(chartContainer, updateChart);

    onMounted(() => {
      // A filter from another page does not apply here
      clearTopSdgFilter();
      updateChart();
    });

    return {
      totalCount,
      chartContainer,
      topSdgFilter,
      clearTopSdgFilter,
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
