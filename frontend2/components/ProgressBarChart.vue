<template>
  <div ref="chart" class="progress-bar-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

const props = defineProps({
  currentXp: {
    type: Number,
    required: true,
  },
  nextLevelXp: {
    type: Number,
    required: true,
  },
  sdgColor: {
    type: String,
    required: true,
  },
});

const chart = ref<HTMLElement | null>(null);

onMounted(() => {
  renderChart();
});

watch(
  () => [props.currentXp, props.nextLevelXp, props.sdgColor],
  () => {
    renderChart();
  }
);

const renderChart = () => {
  if (!chart.value) return;

  const width = 300;            // Width of the progress bar
  const barHeight = 20;         // Height of the bar
  const labelOffset = 25;       // Vertical offset for text labels
  const svgHeight = barHeight + labelOffset; // Total SVG height

  // Clear any existing SVG elements
  d3.select(chart.value).selectAll('*').remove();

  const svg = d3.select(chart.value)
    .append('svg')
    .attr('width', width)
    .attr('height', svgHeight);

  // Calculate progress safely: if nextLevelXp is 0, default to full progress
  const progress = (props.nextLevelXp > 0) ? props.currentXp / props.nextLevelXp : 1;
  const progressWidth = width * Math.min(progress, 1);

  // Draw the background bar
  svg.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', width)
    .attr('height', barHeight)
    .attr('fill', '#e0e0e0')
    .attr('rx', 10)
    .attr('ry', 10);

  // Draw the animated progress bar
  svg.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', 0)
    .attr('height', barHeight)
    .attr('fill', props.sdgColor)
    .attr('rx', 10)
    .attr('ry', 10)
    .transition()
    .duration(1000)
    .attr('width', progressWidth);

  // Left label: Current XP
  svg.append('text')
    .attr('x', 0)
    .attr('y', barHeight + labelOffset - 5)
    .attr('fill', '#000')
    .attr('text-anchor', 'start')
    .style('font-size', '12px')
    .text(`Current XP: ${props.currentXp}`);

  // Right label: Next Level XP
  svg.append('text')
    .attr('x', width)
    .attr('y', barHeight + labelOffset - 5)
    .attr('fill', '#000')
    .attr('text-anchor', 'end')
    .style('font-size', '12px')
    .text(props.nextLevelXp > 0 ? `Next Level: ${props.nextLevelXp}` : "Max Level");
};
</script>

<style scoped>
.progress-bar-chart {
  margin-top: 20px;
}
</style>
