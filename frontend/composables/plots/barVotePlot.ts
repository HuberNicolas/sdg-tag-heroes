import * as d3 from 'd3';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";

export function createBarVotePlot(container, width, height, votesData) {
  d3.select(container).selectAll('*').remove();

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const margin = { top: 20, right: 20, bottom: 20, left: 20 };
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

  // Data for the bar chart
  const data = [
    { label: "Negative", value: -proportions.negative, count: votesData.negative },
    { label: "Positive", value: proportions.positive, count: votesData.positive },
  ];

  // Adjusted scale for width reduction
  const barWidthFactor = 0.6; // Reduces the bar width
  const x = d3.scaleBand()
    .range([0, chartWidth])
    .domain(data.map(d => d.label))
    .padding(barWidthFactor);

  const y = d3.scaleLinear()
    .domain([-1, 1])
    .range([chartHeight, 0]);

  // Tooltip
  const tooltip = d3.select(container)
    .append("div")
    .style("position", "absolute")
    .style("visibility", "hidden")
    .style("background", "#fff")
    .style("border", "1px solid #ccc")
    .style("padding", "5px")
    .style("border-radius", "3px")
    .style("font-size", "12px");

  // Bars for Negative and Positive
  g.selectAll("mybar")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", d => x(d.label))
    .attr("y", d => y(Math.max(0, d.value)))
    .attr("width", x.bandwidth())
    .attr("height", d => Math.abs(y(d.value) - y(0)))
    .attr("fill", d => colors[d.label.toLowerCase()])
    .on("mouseover", (event, d) => {
      tooltip.style("visibility", "visible")
        .text(`${d.label}: ${d.count} Vote(s), ${(Math.abs(d.value) * 100).toFixed(1)}%`);
    })
    .on("mousemove", (event) => {
      tooltip.style("top", `${event.pageY - 10}px`)
        .style("left", `${event.pageX + 10}px`);
    })
    .on("mouseout", () => {
      tooltip.style("visibility", "hidden");
    });

  // Centered Neutral Bar
  const neutralBarHeight = 20;
  const neutralBarY = chartHeight / 2 - neutralBarHeight / 2;

  // Center the neutral bar between Negative and Positive bars
  const neutralStartX = (x("Negative") + x("Positive")) / 2 - (proportions.neutral * chartWidth) / 2;
  const neutralBarLength = proportions.neutral * chartWidth;

  g.append("rect")
    .attr("x", neutralStartX)
    .attr("y", neutralBarY)
    .attr("width", neutralBarLength)
    .attr("height", neutralBarHeight)
    .attr("fill", colors.neutral)
    .on("mouseover", (event) => {
      tooltip.style("visibility", "visible")
        .text(`Neutral: ${votesData.neutral} Vote(s), ${(proportions.neutral * 100).toFixed(1)}%`);
    })
    .on("mousemove", (event) => {
      tooltip.style("top", `${event.pageY - 10}px`)
        .style("left", `${event.pageX + 10}px`);
    })
    .on("mouseout", () => {
      tooltip.style("visibility", "hidden");
    });

  // Horizontal line at zero
  g.append("line")
    .attr("x1", 0)
    .attr("x2", chartWidth)
    .attr("y1", y(0))
    .attr("y2", y(0))
    .attr("stroke", "#000")
    .attr("stroke-width", 1);
}
