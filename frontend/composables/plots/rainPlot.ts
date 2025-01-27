import * as d3 from 'd3';
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { calculateEntropy } from "~/utils/entropy";

export function createRaincloudPlot(container, width, height) {
  const sdgPredictionsStore = useSDGPredictionsStore();

  // Watch for changes in the selected SDG predictions
  sdgPredictionsStore.$subscribe((mutation, state) => {
    if (state.selectedPartitionedSDGPredictions.length > 0) {
      const entropyData = state.selectedPartitionedSDGPredictions.map(prediction => calculateEntropy(prediction));
      renderRaincloudPlot(container, entropyData, 500, 300);
    }
  });

  // Initial render (optional)
  //if (sdgPredictionsStore.selectedPartitionedSDGPredictions.length > 0) {
    //const entropyData = sdgPredictionsStore.selectedPartitionedSDGPredictions.map(prediction => calculateEntropy(prediction));
    //renderRaincloudPlot(container, entropyData, width, height );
  //}
}

function renderRaincloudPlot(container, data, width, height) {
  const margin = { top: 0, right: 0, bottom: 0, left: 0 };
  const totalWidth = width - margin.left - margin.right;
  const totalHeight = height - margin.top - margin.bottom;
  console.log(width, height, totalWidth, totalHeight);

  const segment = totalHeight * 0.25; // y-position density plot
  const size = segment * 0.8; // for density plot

  console.log(`Rendering raincloud plot for container`);

  // Verify and sort the data
  if (!data || data.length === 0) {
    console.error('No data provided for raincloud plot.');
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
  const x = d3.scaleLinear().domain(d3.extent(sortedData) as [number, number]).range([0, totalWidth]);

  // Clear container and append SVG
  d3.select(container).selectAll('*').remove();
  const svg = d3.select(container)
    .append('svg')
    .attr('width', totalWidth + margin.left + margin.right)
    .attr('height', totalHeight + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // Raincloud structure: combine curve, dots, and boxplot
  const raincloud = (selection, data) => {
    selection
      .call(curve, data)
      .call(dots, data)
      .call(boxplot, data);
  };

  // Curve (Density Histogram)
  const curve = (selection, data) => {
    const histogram = d3
      .bin()
      .thresholds(20)(data)
      .map((bin) => bin.length);

    const xScale = d3.scaleLinear().domain([0, histogram.length]).range([0, totalWidth]);
    const yScale = d3.scaleLinear().domain([0, d3.max(histogram)]).range([size, 0]);

    const area = d3
      .area()
      .x((_, i) => xScale(i))
      .y0(yScale(0))
      .y1((d) => yScale(d))
      .curve(d3.curveBasis);

    selection
      .append('path')
      .datum(histogram)
      .attr('d', area)
      .style('fill', 'steelblue')
      .style('opacity', 0.6);
  };

  // Boxplot
  const boxplot = (selection, data) => {
    const y = totalHeight * 0.5;
    const boxHeight = Math.max(0, totalHeight / 12); // Ensure boxHeight is always positive

    selection
      .append('g')
      .classed('boxplot', true)
      .attr('transform', `translate(0, ${y})`)
      .call((g) => {
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
        const width = Math.max(0, x(q3) - x(q1));
        g.append('rect')
          .attr('x', x(q1))
          .attr('y', -boxHeight / 2)
          .attr('width', width)
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
      .attr('r', 5)
      .attr('cx', (d) => x(d)) // Keep x-axis alignment consistent with boxplot and density
      .attr('cy', () => totalHeight * 0.75 + (Math.random() - 0.5) * jitterHeight) // Add random vertical jitter only
      .style('fill', 'steelblue')
      .style('opacity', 0.6)
      .attr('stroke', 'none');
  };

  // Call the raincloud rendering function
  svg.append('g').call(raincloud, sortedData);
}
