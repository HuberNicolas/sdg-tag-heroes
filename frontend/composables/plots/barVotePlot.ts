import * as d3 from 'd3';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";

export function createBarVotePlot(container, width, height, votesData) {
  d3.select(container).selectAll('*').remove();
  console.log("votesData", votesData);

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const margin = { top: 10, right: 10, bottom: 30, left: 40 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const totalVotes = Object.values(votesData).reduce((acc, val) => acc + val, 0) || 1;
  const proportions = {
    positive: votesData.positive / totalVotes,
    neutral: votesData.neutral / totalVotes,
    negative: votesData.negative / totalVotes,
  };

  const colors = { positive: "#3845a0", neutral: "#9E9E9E", negative: "#F44336" };

  let startX = 0;
  Object.entries(proportions).forEach(([category, proportion]) => {
    g.append("rect")
      .attr("x", startX * chartWidth)
      .attr("y", chartHeight / 4)
      .attr("width", proportion * chartWidth)
      .attr("height", chartHeight / 2)
      .attr("fill", colors[category])
      .append("title")
      .text(`${votesData[category]} votes`);

    startX += proportion;
  });

  g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(d3.scaleLinear().domain([0, totalVotes]).range([0, chartWidth])).ticks(5).tickFormat(d3.format("d")));
}
