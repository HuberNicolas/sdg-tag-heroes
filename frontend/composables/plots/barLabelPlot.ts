import * as d3 from 'd3';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";

export function createBarLabelPlot(container, width, height) {
  const labelDecisionsStore = useLabelDecisionsStore();
  const sdgsStore = useSDGsStore();

  labelDecisionsStore.$subscribe((mutation, state) => {
    if (state.selectedSDGLabelDecision && state.userLabels) {
      const labelDistribution = aggregateUserVotes(state.userLabels);
      console.log(labelDistribution);
      updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore);
    }
  });

  if (labelDecisionsStore.selectedSDGLabelDecision && labelDecisionsStore.userLabels) {
    const labelDistribution = aggregateUserVotes(labelDecisionsStore.userLabels);
    console.log(labelDistribution);
    updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore);
  }
}

function aggregateUserVotes(userLabels) {
  const voteCounts = {};
  userLabels.forEach(label => {
    const votedLabel = label.votedLabel;
    if ((votedLabel >= 1 && votedLabel <= 17) || votedLabel === -1) {
      voteCounts[votedLabel] = (voteCounts[votedLabel] || 0) + 1;
    }
  });
  return Object.entries(voteCounts).map(([label, count]) => ({ label: Number(label), count }));
}

function updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore) {
  d3.select(container).selectAll('*').remove();

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const margin = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand()
    .domain(labelDistribution.map(d => d.label === -1 ? 'Not relevant' : `SDG ${d.label}`))
    .range([0, chartWidth])
    .padding(0.3);

  const y = d3.scaleLinear()
    .domain([0, d3.max(labelDistribution, d => d.count)])
    .nice()
    .range([chartHeight, 0]);

  g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .style("text-anchor", "middle");

  g.append("g")
    .call(d3.axisLeft(y).ticks(d3.max(labelDistribution, d => d.count)).tickFormat(d3.format("d")));

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
