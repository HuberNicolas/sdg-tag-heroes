import * as d3 from 'd3';

// Function to create a box plot in a specified container
export function createBoxPlot(containerId: string, data: number[], options: { width: number; height: number }) {
  const margin = { top: 10, right: 30, bottom: 30, left: 40 };
  const width = options.width - margin.left - margin.right;
  const height = options.height - margin.top - margin.bottom;


  // Remove any previous SVG in the container
  d3.select(`#${containerId}`).selectAll("*").remove();

  // Append the SVG object to the container
  const svg = d3
    .select(`#${containerId}`)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // Compute quartiles, median, and interquartile range
  const sortedData = data.sort(d3.ascending);
  const q1 = d3.quantile(sortedData, 0.25) ?? 0;
  const median = d3.quantile(sortedData, 0.5) ?? 0;
  const q3 = d3.quantile(sortedData, 0.75) ?? 0;
  const interQuantileRange = q3 - q1;
  const min = Math.max(d3.min(sortedData) ?? 0, q1 - 1.5 * interQuantileRange);
  const max = Math.min(d3.max(sortedData) ?? 0, q3 + 1.5 * interQuantileRange);

  // Create scales
  const y = d3.scaleLinear().domain([min - 1, max + 1]).range([height, 0]);
  const x = d3.scaleBand().domain(['Box']).range([0, width]).padding(0.5);

  // Add Y axis
  svg.append('g').call(d3.axisLeft(y));

  // Add a rectangle for the main box
  svg
    .append('rect')
    .attr('x', x('Box') - 50 / 2)
    .attr('y', y(q3))
    .attr('height', y(q1) - y(q3))
    .attr('width', 50)
    .attr('stroke', 'black')
    .style('fill', '#69b3a2');

  // Add median line
  svg
    .append('line')
    .attr('x1', x('Box') - 50 / 2)
    .attr('x2', x('Box') + 50 / 2)
    .attr('y1', y(median))
    .attr('y2', y(median))
    .attr('stroke', 'black');

  // Add min and max lines
  svg
    .append('line')
    .attr('x1', x('Box'))
    .attr('x2', x('Box'))
    .attr('y1', y(min))
    .attr('y2', y(max))
    .attr('stroke', 'black');

  // Add individual points with jitter
  const jitterWidth = 20; // Adjust jitter width for spread
  svg
    .selectAll('indPoints')
    .data(data)
    .enter()
    .append('circle')
    .attr('cx', () => x('Box')! - jitterWidth / 2 + Math.random() * jitterWidth)
    .attr('cy', d => y(d))
    .attr('r', 1)
    .style('fill', 'white')
    .attr('stroke', 'black');
}
