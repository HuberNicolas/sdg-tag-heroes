<template>
  <div class="flex flex-col items-center justify-center bg-gray-100 p-4 rounded-lg shadow-md w-full">
    <!-- D3 Raincloud Plot -->
    <p class="text-sm text-gray-600">
      Labeling Effort: XP Distribution of Your Selection
    </p>
    <div ref="chartContainer" class="w-full h-80 relative" ></div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch, computed } from "vue";
import * as d3 from "d3";
import { useSDGPredictionsStore } from "@/stores/sdgPredictions";
import { usePublicationsStore } from "@/stores/publications";
import {useSDGsStore} from "@/stores/sdgs";
import {useGameStore} from "@/stores/game";

// Initialize Pinia stores inside the setup function
const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const sdgsStore = useSDGsStore();
const gameStore = useGameStore();
const sdg = gameStore.getSDG;
const selectedSDGColor = computed(() => {
  const sdg = gameStore.getSDG;
  return sdg ? sdgsStore.getColorBySDG(sdg) : "#000000"; // Default color (black) if not initialized
});


// Reactive state
const chartContainer = ref(null);
const hoveredEntropy = ref(null);

// Watch for changes in the hovered publication
watch(() => publicationsStore.hoveredPublication, (newVal) => {
  if (newVal) {
    const prediction = sdgPredictionsStore.selectedPartitionedSDGPredictions.find(
      p => p.publicationId === newVal.publicationId
    );
    hoveredEntropy.value = prediction ? parseInt(Math.round(prediction.entropy * 100)) : null;
  } else {
    hoveredEntropy.value = null;
  }
  updateChart();
}, { deep: true });

// Compute entropy values from predictions
const entropyData = computed(() => {
  return sdgPredictionsStore.selectedPartitionedSDGPredictions.map(prediction => parseInt(Math.round(prediction.entropy * 100)));
});

// Persistent jitter mapping
const jitterMap = new Map();

// Function to update the Raincloud Plot
const updateChart = () => {
  if (!chartContainer.value) return;

  const data = entropyData.value;
  const width = chartContainer.value.clientWidth;
  const height = 240;
  const margin = { top: 5, right: 80, bottom: 50, left: 80 };

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

  const entropyLookup = new Map();
  sdgPredictionsStore.selectedPartitionedSDGPredictions.forEach(prediction => {
    const entropyValue = parseInt(Math.round(prediction.entropy * 100));
    entropyLookup.set(entropyValue, prediction);
  });


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
  const densityData = d3.histogram()
    .domain(xScale.domain()) // Match x-axis with the boxplot
    .thresholds(xScale.ticks(30)) // Ensure the same binning resolution
    (sortedData);

// Compute density
  const kde = densityData.map(bin => ({
    x: (bin.x0 + bin.x1) / 2,  // Midpoint of bin
    y: bin.length
  }));

  const yScaleHist = d3.scaleLinear()
    .domain([0, d3.max(kde, d => d.y)])
    .range([40, 0]);

  const area = d3.area()
    .x(d => xScale(d.x)) // Use the same xScale
    .y0(yScaleHist(0))
    .y1(d => yScaleHist(d.y))
    .curve(d3.curveBasis);

  svg.append("path")
    .datum(kde)
    .attr("d", area)
    .style("fill", "grey")
    .style("opacity", 0.6);


  // Highlight the line in the distribution for hovered publication
  if (hoveredEntropy.value !== null) {
    svg.append("line")
      .attr("x1", xScale(hoveredEntropy.value))
      .attr("x2", xScale(hoveredEntropy.value))
      .attr("y1", 0)
      .attr("y2", height - margin.bottom)
      .attr("stroke", selectedSDGColor.value)
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "5,5");
  }

  // Boxplot with whiskers
  const boxHeight = 8;
  const yBoxplot = height * 0.45;

  // Whiskers
  svg.append("line")
    .attr("x1", xScale(min))
    .attr("x2", xScale(min))
    .attr("y1", yBoxplot - boxHeight)
    .attr("y2", yBoxplot + boxHeight)
    .attr("stroke", "black");

  svg.append("line")
    .attr("x1", xScale(max))
    .attr("x2", xScale(max))
    .attr("y1", yBoxplot - boxHeight)
    .attr("y2", yBoxplot + boxHeight)
    .attr("stroke", "black");

  svg.append("line").attr("x1", xScale(min)).attr("x2", xScale(max)).attr("y1", yBoxplot).attr("y2", yBoxplot).attr("stroke", "black");
  svg.append("rect").attr("x", xScale(q1)).attr("y", yBoxplot - boxHeight / 2)
    .attr("width", xScale(q3) - xScale(q1)).attr("height", boxHeight)
    .attr("fill", "grey").attr("opacity", 0.6);
  svg.append("line").attr("x1", xScale(median)).attr("x2", xScale(median)).attr("y1", yBoxplot - boxHeight / 2).attr("y2", yBoxplot + boxHeight / 2).attr("stroke", "black");


  // Create a function to generate hexagon points
  function hexagonPoints(x, y, radius) {
    const points = [];
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i;
      points.push([
        x + radius * Math.cos(angle),
        y + radius * Math.sin(angle)
      ]);
    }
    return points;
  }

// Replace the two polygon sections with this code
// Left whisker marker (at minimum value)
  const leftHexPoints = hexagonPoints(xScale(min)-50, yBoxplot, 10);
  const leftPathData = `M ${leftHexPoints.map(p => p.join(',')).join(' L ')} Z`;
  svg.append("path")
    .attr("d", leftPathData)
    .attr("fill", selectedSDGColor.value);

// Right whisker marker (at maximum value)
  const rightHexPoints = hexagonPoints(xScale(max)+50, yBoxplot, 25);
  const rightPathData = `M ${rightHexPoints.map(p => p.join(',')).join(' L ')} Z`;
  svg.append("path")
    .attr("d", rightPathData)
    .attr("fill", selectedSDGColor.value);


  // Left whisker marker label
  svg.append("text")
    .attr("x", xScale(min)-50)
    .attr("y", yBoxplot + 20 + 20) // 15px below the hexagon
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .style("font-size", "12px")
    .text("Low XP");

// Right whisker marker label
  svg.append("text")
    .attr("x", xScale(max)+50)
    .attr("y", yBoxplot + 20 + 20) // 15px below the hexagon
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .style("font-size", "12px")
    .text("High XP");


  // Position the labels **above** the whiskers
  const labelYOffset = -15; // Move labels up
  const valueYOffset = 20;  // Move numerical values down

// Labels (Min, Median, Max) above whiskers
  svg.append("text")
    .attr("x", xScale(min))
    .attr("y", yBoxplot + labelYOffset)
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .style("font-weight", "bold")
    .text("Min");

  svg.append("text")
    .attr("x", xScale(median))
    .attr("y", yBoxplot + labelYOffset)
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .style("font-weight", "bold")
    .text("Median");

  svg.append("text")
    .attr("x", xScale(max))
    .attr("y", yBoxplot + labelYOffset)
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .style("font-weight", "bold")
    .text("Max");

// Numerical values **below** whiskers
  svg.append("text")
    .attr("x", xScale(min))
    .attr("y", yBoxplot + valueYOffset)
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .text(min.toFixed(0));

  svg.append("text")
    .attr("x", xScale(median))
    .attr("y", yBoxplot + valueYOffset)
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .text(median.toFixed(0));

  svg.append("text")
    .attr("x", xScale(max))
    .attr("y", yBoxplot + valueYOffset)
    .attr("text-anchor", "middle")
    .attr("fill", "black")
    .text(max.toFixed(0));


  // Highlight the line in the boxplot for hovered publication
  if (hoveredEntropy.value !== null) {
    svg.append("line")
      .attr("x1", xScale(hoveredEntropy.value))
      .attr("x2", xScale(hoveredEntropy.value))
      .attr("y1", yBoxplot - boxHeight / 2)
      .attr("y2", yBoxplot + boxHeight / 2)
      .attr("stroke", selectedSDGColor.value)
      .attr("stroke-width", 2);
  }
  // Assign persistent jitter values
  const jitterHeight = 30;
  sortedData.forEach(d => {
    if (!jitterMap.has(d)) {
      jitterMap.set(d, (Math.random() - 0.5) * jitterHeight);
    }
  });

  console.log(sortedData);

  // Dots with tooltip
  svg.selectAll("circle")
    .data(sortedData)
    .enter()
    .append("circle")
    .attr("r", 5)
    .attr("cx", d => xScale(d))
    .attr("cy", d => height * 0.7 + jitterMap.get(d)) // Use stored jitter value
    .style("fill", d => {
      const prediction = entropyLookup.get(d);
      if (!prediction) return "grey";

      // Extract highest SDG score
      let highestSDG = Object.keys(prediction)
        .filter(key => key.startsWith("sdg"))
        .map(key => ({ id: parseInt(key.replace("sdg", "")), value: prediction[key] }))
        .reduce((max, sdg) => (sdg.value > max.value ? sdg : max), { id: null, value: 0 });

      return highestSDG.id ? sdgsStore.getColorBySDG(highestSDG.id) : "grey";
    })
    .style("opacity", d => d === hoveredEntropy.value ? 1 : 0.6)
    /* Deactivate hover
    .on("mouseover", function(event, d) {
      tooltip.style("visibility", "visible").html(`Value: ${d.toFixed(2)}`)
        .style("left", `${event.pageX + 10}px`).style("top", `${event.pageY}px`);
      d3.select(this).attr("stroke", "black").attr("stroke-width", 1);
    })
    .on("mouseout", function() {
      tooltip.style("visibility", "hidden");
      d3.select(this).attr("stroke", "none");
    });
    */


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
</script>

<style scoped>
/* Ensure full width */
.w-full {
  width: 100%;
}


</style>
