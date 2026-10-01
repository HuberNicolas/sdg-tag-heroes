<template>
  <!-- Share of the community labels per SDG: a ring with the total in the middle -->
  <div class="relative flex flex-col items-center">
    <div v-if="labelDecisionsStore.totalVotes > 0" ref="chartContainer" class="relative" />

    <div v-else class="flex h-[132px] w-[132px] flex-col items-center justify-center gap-1 rounded-full border border-dashed border-line-strong text-center">
      <Icon name="mdi-hexagon-outline" class="h-5 w-5 text-accent" />
      <p class="font-mono text-[11px] leading-tight text-fg-dim">no labels yet<br>be the first</p>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";
import * as d3 from "d3";

const labelDecisionsStore = useLabelDecisionsStore();
const sdgsStore = useSDGsStore();
const chartContainer = ref(null);

const NOT_RELEVANT = "rgb(var(--c-fg-faint))";

function drawDonutChart() {
  if (!chartContainer.value) return;
  d3.select(chartContainer.value).selectAll("*").remove(); // Clear previous chart

  if (!labelDecisionsStore.totalVotes) return;

  const size = 132;
  const radius = size / 2;

  const svg = d3.select(chartContainer.value)
    .append("svg")
    .attr("width", size)
    .attr("height", size)
    .attr("viewBox", `0 0 ${size} ${size}`)
    .append("g")
    .attr("transform", `translate(${radius},${radius})`);

  const data = labelDecisionsStore.voteDistribution;
  const pie = d3.pie().value(d => d.value).sort((a, b) => b.value - a.value).padAngle(0.025);
  const data_ready = pie(Object.entries(data).map(([key, value]) => ({ key: Number(key), value })));

  const arc = d3.arc().innerRadius(radius * 0.66).outerRadius(radius - 4).cornerRadius(3);
  const arcHover = d3.arc().innerRadius(radius * 0.64).outerRadius(radius).cornerRadius(3);

  const getSDGColor = (label) => (label === -1 ? NOT_RELEVANT : sdgsStore.getColorBySDG(Number(label)) || NOT_RELEVANT);
  const getTitle = (label) => (label === -1 ? "Not relevant" : `SDG ${label} · ${sdgsStore.getShortTitleBySDG(label)}`);

  // Centre: total, replaced by the hovered slice
  const centreValue = svg.append("text").attr("class", "donut__value").attr("dy", "0.1em").text(labelDecisionsStore.totalVotes);
  const centreLabel = svg.append("text").attr("class", "donut__label").attr("dy", "1.6em").text("labels");

  svg.selectAll("path")
    .data(data_ready)
    .enter()
    .append("path")
    .attr("d", arc)
    .attr("fill", d => getSDGColor(d.data.key))
    .attr("class", "donut__slice")
    .on("mouseenter", function (event, d) {
      d3.select(this).transition().duration(150).attr("d", arcHover);
      centreValue.text(`${Math.round((d.value / labelDecisionsStore.totalVotes) * 100)}%`).style("fill", getSDGColor(d.data.key));
      centreLabel.text(d.data.key === -1 ? "not relevant" : `sdg ${d.data.key}`);
    })
    .on("mouseleave", function () {
      d3.select(this).transition().duration(150).attr("d", arc);
      centreValue.text(labelDecisionsStore.totalVotes).style("fill", null);
      centreLabel.text("labels");
    })
    .append("title")
    .text(d => `${getTitle(d.data.key)}: ${d.value} of ${labelDecisionsStore.totalVotes} labels`);
}

// Watch for changes in vote data
watch(() => labelDecisionsStore.voteDistribution, async () => {
  await nextTick();
  drawDonutChart();
}, { deep: true });

onMounted(() => {
  if (labelDecisionsStore.totalVotes) {
    drawDonutChart();
  }
});
</script>

<style scoped>
:deep(.donut__slice) {
  stroke: rgb(var(--c-surface));
  stroke-width: 1;
  cursor: pointer;
}
:deep(.donut__value) {
  fill: rgb(var(--c-fg));
  font: 700 22px var(--font-mono);
  text-anchor: middle;
}
:deep(.donut__label) {
  fill: rgb(var(--c-fg-faint));
  font: 500 10.5px var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  text-anchor: middle;
}
</style>
