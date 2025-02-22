import * as d3 from 'd3';

export function createBarVotePlot(container, width, height, votesData) {
  d3.select(container).selectAll('*').remove();

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const margin = { top: 20, right: 30, bottom: 50, left: 30 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const totalVotes = votesData.positive + votesData.negative || 1;
  const proportions = {
    positive: votesData.positive / totalVotes,
    negative: votesData.negative / totalVotes,
  };

  // Use grayscale encoding
  const colors = { positive: "#6D6D6D", negative: "#B0B0B0" };

  const data = [
    { label: "Positive", value: proportions.positive, count: votesData.positive },
    { label: "Negative", value: -proportions.negative, count: votesData.negative }
  ];

  const x = d3.scaleLinear()
    .domain([-1, 1])
    .range([0, chartWidth]);

  const y = d3.scaleBand()
    .range([0, chartHeight])
    .domain(["Votes"])
    .padding(0.4);

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

  // Bars
  g.selectAll(".bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("y", y("Votes"))
    .attr("x", d => d.value >= 0 ? x(0) : x(d.value))
    .attr("width", d => Math.abs(x(d.value) - x(0)))
    .attr("height", y.bandwidth())
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

  // Axes
  g.append("g")
    .attr("transform", `translate(0,${chartHeight})`)
    .call(d3.axisBottom(x).tickValues([-1, -0.5, 0, 0.5, 1])
      .tickFormat(d => `${Math.abs(d * 100)}%`));

  //g.append("g")
    //.call(d3.axisLeft(y).tickFormat(() => ""));

  // Add X-axis labels
  g.append("text")
    .attr("x", x(-0.5))
    .attr("y", chartHeight + 30)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .text("Negative");

  g.append("text")
    .attr("x", x(0.5))
    .attr("y", chartHeight + 30)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .text("Positive");

  // Vertical zero line
  g.append("line")
    .attr("x1", x(0))
    .attr("x2", x(0))
    .attr("y1", 0)
    .attr("y2", chartHeight)
    .attr("stroke", "#000")
    .attr("stroke-width", 1);
}
