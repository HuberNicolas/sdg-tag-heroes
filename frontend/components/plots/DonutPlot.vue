<template>
  <div class="flex flex-col items-center">
    <p>Total Votes: {{ labelDecisionsStore.totalVotes }}</p>

    <div v-if="labelDecisionsStore.totalVotes > 0" ref="chartContainer"></div>
    <p v-else >No votes available.</p>
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

  const width = 150, height = 150, margin = 20;
  const radius = Math.min(width, height) / 3 - margin;

  const svg = d3.select(chartContainer.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width / 2},${height / 2})`);

  const data = labelDecisionsStore.voteDistribution;

  const pie = d3.pie().value(d => d.value);

  const data_ready = pie(Object.entries(data).map(([key, value]) => ({ key: Number(key), value })));

  const arc = d3.arc().innerRadius(radius * 0.3).outerRadius(radius * 0.7);
  const outerArc = d3.arc().innerRadius(radius * 0.7).outerRadius(radius * 0.8);

  function getSDGColor(label) {
    return sdgsStore.getColorBySDG(Number(label)) || "#CCCCCC"; // Default gray if no color is found
  }

  svg.selectAll("allSlices")
    .data(data_ready)
    .enter()
    .append("path")
    .attr("d", arc)
    .attr("fill", d => getSDGColor(d.data.key))
    .attr("stroke", "white")
    .style("stroke-width", "2px")
    .style("opacity", 0.7);

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
    .style("font-weight", "bold");
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
