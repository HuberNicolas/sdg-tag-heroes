import * as d3 from 'd3';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";

export function createBarLabelPlot(container, width, height) {
  const labelDecisionsStore = useLabelDecisionsStore();
  const sdgsStore = useSDGsStore();

  function updateChart() {
    if (labelDecisionsStore.selectedSDGLabelDecision && labelDecisionsStore.userLabels) {
      const labelDistribution = aggregateUserVotes(labelDecisionsStore.userLabels, labelDecisionsStore.showAllSDGUserLabels);
      updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore);
    }
  }

  // Subscribe to Pinia store updates and update the plot when data changes
  labelDecisionsStore.$subscribe((mutation, state) => {
    updateChart();
  });

  // Watch `showAllSDGUserLabels` and update chart when toggled
  watch(
    () => labelDecisionsStore.showAllSDGUserLabels,
    () => {
      updateChart();
    }
  );

  // Initial rendering of the chart
  updateChart();
}
/**
 * Aggregates user votes, either showing all or only the latest vote per user.
 */
export function aggregateUserVotes(userLabels, showAll) {
  const latestLabels = new Map();

  if (!showAll) {
    // Keep only the latest SDG label per user
    userLabels.forEach(label => {
      if (
        !latestLabels.has(label.userId) ||
        new Date(label.createdAt) > new Date(latestLabels.get(label.userId).createdAt)
      ) {
        latestLabels.set(label.userId, label);
      }
    });
  }

  // Use either all labels or the latest one per user
  const filteredLabels = showAll ? userLabels : Array.from(latestLabels.values());

  // Count votes for each SDG label
  const voteCounts = {};
  filteredLabels.forEach(label => {
    const votedLabel = label.votedLabel;
    if ((votedLabel >= 1 && votedLabel <= 17) || votedLabel === -1) {
      voteCounts[votedLabel] = (voteCounts[votedLabel] || 0) + 1;
    }
  });

  return Object.entries(voteCounts).map(([label, count]) => ({ label: Number(label), count }));
}

/**
 * Updates the D3 bar chart with new data.
 */
export function updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore) {
  // Clear previous chart
  d3.select(container).selectAll('*').remove();

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const margin = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  // X-Axis: SDG Labels
  const x = d3.scaleBand()
    .domain(labelDistribution.map(d => d.label === -1 ? 'Not relevant' : `SDG ${d.label}`))
    .range([0, chartWidth])
    .padding(0.3);

  // Y-Axis: Number of votes
  const y = d3.scaleLinear()
    .domain([0, d3.max(labelDistribution, d => d.count) || 1])
    .nice()
    .range([chartHeight, 0]);

  // Draw X-Axis
  g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .style("text-anchor", "middle");

  // Draw Y-Axis
  g.append("g")
    .call(d3.axisLeft(y).ticks(d3.max(labelDistribution, d => d.count) || 1).tickFormat(d3.format("d")));

  // Draw bars
  g.selectAll(".bar")
    .data(labelDistribution)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", d => x(d.label === -1 ? 'Not relevant' : `SDG ${d.label}`))
    .attr("y", d => y(d.count))
    .attr("width", x.bandwidth())
    .attr("height", d => chartHeight - y(d.count))
    .attr("fill", d => d.label === -1 ? '#CCCCCC' : sdgsStore.getColorBySDG(d.label) || '#CCCCCC')
    .append("title")
    .text(d => `${d.count} votes`);
}
