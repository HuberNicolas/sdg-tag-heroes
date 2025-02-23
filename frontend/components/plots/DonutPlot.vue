<template>
  <div class="flex flex-col items-center">
    <p>Total Community Labels: {{ labelDecisionsStore.totalVotes }}</p>

    <div v-if="labelDecisionsStore.totalVotes > 0" ref="chartContainer"></div>

    <div v-else class="flex flex-col items-center justify-center h-full">
      <p>Be the first Labeler.</p>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, watch } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";
import * as d3 from "d3";

const labelDecisionsStore = useLabelDecisionsStore();
const sdgsStore = useSDGsStore();
const chartContainer = ref(null);

function drawDonutChart() {
  d3.select(chartContainer.value).selectAll("*").remove(); // Clear previous chart

  if (!labelDecisionsStore.totalVotes) return;

  const width = 225, height = 225, margin = 5;
  const radius = Math.min(width, height) / 3 - margin;

  const svg = d3.select(chartContainer.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width / 2},${height / 3})`);

  const data = labelDecisionsStore.voteDistribution;

  const pie = d3.pie().value(d => d.value);

  const data_ready = pie(Object.entries(data).map(([key, value]) => ({ key: Number(key), value })));

  const arc = d3.arc().innerRadius(radius * 0.3).outerRadius(radius * 0.7);
  const outerArc = d3.arc().innerRadius(radius * 0.7).outerRadius(radius * 0.8);

  function getSDGColor(label) {
    return sdgsStore.getColorBySDG(Number(label)) || "#CCCCCC"; // Default gray if no color is found
  }

  // Create tooltip div
  const tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .style("pointer-events", "none")
    .style("position", "absolute")
    .style("padding", "8px")
    .style("background-color", "rgba(255, 255, 255, 0.95)")
    .style("border-radius", "4px")
    .style("font-size", "14px")
    .style("box-shadow", "0 2px 4px rgba(0, 0, 0, 0.1)");

  svg.selectAll("allSlices")
    .data(data_ready)
    .enter()
    .append("path")
    .attr("d", arc)
    .attr("fill", d => getSDGColor(d.data.key))
    .attr("stroke", "white")
    .style("stroke-width", "2px")
    .style("opacity", 0.8)
    // Replace the existing mouseover/mouseout handlers with:
    .on("mouseover", function(event, d) {
      // Get SDG details
      const sdgId = d.data.key;
      const shortTitle = sdgId === -1 ? "Not Relevant" : sdgsStore.getShortTitleBySDG(sdgId);
      const color = sdgId === -1 ? "#CCCCCC" : sdgsStore.getColorBySDG(sdgId) || "#CCCCCC";

      // Compute percentage
      const percentage = ((d.value / labelDecisionsStore.totalVotes) * 100).toFixed(1);

      // Create tooltip content
      const text = `
    <div style="display: flex; align-items: center;">
      <div style="width: 12px; height: 12px; background-color: ${color}; border-radius: 50%; margin-right: 8px;"></div>
      <div>
        <strong>${sdgId === -1 ? "Not Relevant" : `SDG ${sdgId}`}:</strong> ${d.value}/${labelDecisionsStore.totalVotes} Labels
        <br>
        <span style="font-size: 12px; font-weight: bold; color: ${color};">${shortTitle}</span>
      </div>
    </div>
  `;

      tooltip.transition()
        .duration(200)
        .style("opacity", 1);

      tooltip.html(text)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");

      // Highlight segment
      d3.select(this)
        .transition()
        .duration(200)
        .attr("fill-opacity", 1);
    })

    .on("mouseout", function() {
      // Hide tooltip properly
      tooltip.transition()
        .duration(200)
        .style("opacity", 0)
        .on("end", function () {
          tooltip.style("left", "-9999px"); // Move out of view
          tooltip.style("top", "-9999px");  // Move out of view
        });

      // Reset segment opacity
      d3.select(this)
        .transition()
        .duration(200)
        .attr("fill-opacity", 0.8);
    });

  svg.selectAll("allPolylines")
    .data(data_ready)
    .enter()
    .append("polyline")
    .attr("stroke", "black")
    .style("fill", "none")
    .attr("stroke-width", 1)
    .attr("points", d => {
      const posA = arc.centroid(d);
      const posB = outerArc.centroid(d);
      const posC = outerArc.centroid(d);
      const midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
      posC[0] = radius * 0.95 * (midangle < Math.PI ? 1 : -1);
      return [posA, posB, posC];
    });

  svg.selectAll("allLabels")
    .data(data_ready)
    .enter()
    .append("text")
    .text(d => (d.data.key === -1 ? "Not Relevant" : `SDG ${d.data.key}`))
    .attr("transform", d => {
      const pos = outerArc.centroid(d);
      const midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
      pos[0] = radius * 0.99 * (midangle < Math.PI ? 1 : -1);
      return `translate(${pos})`;
    })
    .style("text-anchor", d => {
      const midangle = d.startAngle + (d.endAngle - d.startAngle) / 2;
      return midangle < Math.PI ? "start" : "end";
    })
    .style("font-size", "12px")
    .style("font-weight", "bold")
    .style("fill", d => getSDGColor(d.data.key)); // Add this line
}

// Watch for changes in vote data
watch(() => labelDecisionsStore.voteDistribution, drawDonutChart, { deep: true });

onMounted(() => {
  if (labelDecisionsStore.totalVotes) {
    drawDonutChart();
  }
});
</script>

<style scoped>
</style>
