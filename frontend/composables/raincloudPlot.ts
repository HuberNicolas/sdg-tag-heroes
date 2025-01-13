import * as d3 from 'd3';

// Function to create a raincloud plot in a specified container
export function createRaincloudPlot(containerId: string, data: number[], options: { width: number; height: number }) {
  const margin = { top: 20, right: 20, bottom: 20, left: 20 };
  const total_width = options.width - margin.left - margin.right;
  const height = options.height - margin.top - margin.bottom;

  const width = total_width - margin.left - margin.right
  const segment = height * 0.25 // y-position density plot
  const size = segment * 0.8 // for density plot

  console.log(`Rendering raincloud plot for container: #${containerId}`);

  // Verify container existence
  const container = d3.select(`#${containerId}`);
  if (container.empty()) {
    console.error(`Container #${containerId} does not exist.`);
    return;
  }

  // Remove any previous SVG in the container
  container.selectAll('*').remove();

  // Append the SVG object to the container
  const svg = container
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // Verify and sort the data
  if (!data || data.length === 0) {
    console.error(`No data provided for container: #${containerId}`);
    return;
  }

  const sortedData = data.sort(d3.ascending);
  console.log('Data passed to the plot:', sortedData);

  const q1 = d3.quantile(sortedData, 0.25) ?? 0;
  const median = d3.quantile(sortedData, 0.5) ?? 0;
  const q3 = d3.quantile(sortedData, 0.75) ?? 0;
  const iqr = q3 - q1;
  const min = Math.max(d3.min(sortedData) ?? 0, q1 - 1.5 * iqr);
  const max = Math.min(d3.max(sortedData) ?? 0, q3 + 1.5 * iqr);

  // Create scales
  const x = d3.scaleLinear().domain(d3.extent(sortedData) as [number, number]).range([0, width]);

  // Raincloud structure: combine curve, dots, and boxplot
  const raincloud = (selection, data) => {
    selection
      .call(curve, data)
      .call(dots, data)
      .call(boxplot, data);
  };

  // Curve (Density Histogram)
  const curve = (selection, data) => {
    const histogram = d3.histogram()
      .thresholds(20)
      (data)
      .map(bin => bin.length)
    const x = d3.scaleLinear()
      .domain([0, histogram.length])
      .range([0, width])
    const y = d3.scaleLinear()
      .domain([0, d3.max(histogram)])
      .range([size, 0])
    const area = d3.area()
      .y0(y)
      .y1(size)
      .x((d, i) => x(i))
      .curve(d3.curveBasis)
    selection.append('g')
      .classed('curve', true)
      .datum(histogram)
      .append('path')
      .attr('d', area)
      .style('fill', 'steelblue')
      .style('opacity', 0.6)
  }

  // Boxplot
  const boxplot = (selection, data) => {
    const y = height * 0.5;
    const boxHeight = height / 12;

    selection
      .append('g')
      .classed('boxplot', true)
      .attr('transform', `translate(0, ${y})`)
      .call(g => {
        // Min/Max lines (Whiskers)
        g.append('line')
          .attr('x1', x(min))
          .attr('x2', x(min))
          .attr('y1', -boxHeight / 2)
          .attr('y2', boxHeight / 2)
          .attr('stroke', 'black');

        g.append('line')
          .attr('x1', x(max))
          .attr('x2', x(max))
          .attr('y1', -boxHeight / 2)
          .attr('y2', boxHeight / 2)
          .attr('stroke', 'black');

        g.append('line')
          .attr('x1', x(min))
          .attr('x2', x(max))
          .attr('y1', 0)
          .attr('y2', 0)
          .attr('stroke', 'black');

        // Box
        g.append('rect')
          .attr('x', x(q1))
          .attr('y', -boxHeight / 2)
          .attr('width', x(q3) - x(q1))
          .attr('height', boxHeight)
          .attr('fill', 'steelblue')
          .attr('opacity', 0.6);

        // Median line
        g.append('line')
          .attr('x1', x(median))
          .attr('x2', x(median))
          .attr('y1', -boxHeight / 2)
          .attr('y2', boxHeight / 2)
          .attr('stroke', 'black');
      });
  };

  // Dots (Raw Data Points)
  const dots = (selection, data) => {
    const jitterHeight = 40; // Controls vertical jitter
    selection
      .append('g')
      .classed('dots', true)
      .selectAll('circle')
      .data(data)
      .enter()
      .append('circle')
      .attr('r', 2)
      .attr('cx', d => x(d)) // Keep x-axis alignment consistent with boxplot and density
      .attr('cy', () => height * 0.75 + (Math.random() - 0.5) * jitterHeight) // Add random vertical jitter only
      .style('fill', 'steelblue')
      .style('opacity', 0.6)
      .attr('stroke', 'none');
  };




  // Call the raincloud rendering function
  svg.append('g').call(raincloud, sortedData);
}
