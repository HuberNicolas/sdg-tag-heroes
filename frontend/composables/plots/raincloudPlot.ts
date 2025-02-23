import * as d3 from 'd3';
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { calculateEntropy } from "~/utils/entropy";

export function createRaincloudPlot(container, width, height) {
  const sdgPredictionsStore = useSDGPredictionsStore();

  // Watch for changes in the selected SDG predictions
  sdgPredictionsStore.$subscribe((mutation, state) => {
    if (state.selectedPartitionedSDGPredictions.length > 0) {
      const entropyData = state.selectedPartitionedSDGPredictions.map(prediction => calculateEntropy(prediction));
      renderRaincloudPlot(container, entropyData, 200, 200);
    }
  });

  // Initial render (optional)
  //if (sdgPredictionsStore.selectedPartitionedSDGPredictions.length > 0) {
    //const entropyData = sdgPredictionsStore.selectedPartitionedSDGPredictions.map(prediction => calculateEntropy(prediction));
    //renderRaincloudPlot(container, entropyData, width, height );
  //}
}

function renderRaincloudPlot(container, data, width, height) {
  console.log(data)
  const margin = { top: 20, right: 20, bottom: 20, left: 20 }; // Add some margin for labels
  const totalWidth = width - margin.left - margin.right;
  const totalHeight = height - margin.top - margin.bottom;

  // Divide the total height into three equal segments
  const segmentHeight = totalHeight / 3;

  // Verify and sort the data
  if (!data || data.length === 0) {
    console.error('No data provided for raincloud plot.');
    return;
  }

  const sortedData = data.sort(d3.ascending);

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

  // Curve (Density Histogram) - Top 1/3
  const curve = (selection, data) => {
    const histogram = d3
      .bin()
      .thresholds(20)(data)
      .map((bin) => bin.length);

    const xScale = d3.scaleLinear().domain([0, histogram.length]).range([0, totalWidth]);
    const yScale = d3.scaleLinear().domain([0, d3.max(histogram)]).range([segmentHeight, 0]);

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
      .style('fill', 'grey')
      .style('opacity', 0.6)
      .attr('transform', `translate(0, 0)`) // Position in top segment
      .attr('opacity', 0)
      .transition()
      .duration(1000)
      .attr('opacity', 1);

  };

  // Boxplot - Middle 1/3
  const boxplot = (selection, data) => {
    const y = segmentHeight; // Position in the middle segment
    const boxHeight = segmentHeight * 0.5; // Adjust box height to fit within the segment

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

        // Add labels for whiskers
        g.append('text')
          .attr('x', x(min))
          .attr('y', -boxHeight)
          .text(`Min: ${min.toFixed(2)}`)
          .attr('font-size', '10px')
          .attr('text-anchor', 'middle');

        g.append('text')
          .attr('x', x(max))
          .attr('y', -boxHeight)
          .text(`Max: ${max.toFixed(2)}`)
          .attr('font-size', '10px')
          .attr('text-anchor', 'middle');

        // Box
        const width = Math.max(0, x(q3) - x(q1));
        g.append('rect')
          .attr('x', x(q1))
          .attr('y', -boxHeight / 2)
          .attr('width', width)
          .attr('height', boxHeight)
          .attr('fill', 'grey')
          .attr('opacity', 0.6);

        // Median line
        g.append('line')
          .attr('x1', x(median))
          .attr('x2', x(median))
          .attr('y1', -boxHeight / 2)
          .attr('y2', boxHeight / 2)
          .attr('stroke', 'black');

        // Add median label
        g.append('text')
          .attr('x', x(median))
          .attr('y', boxHeight + 10)
          .text(`Median: ${median.toFixed(2)}`)
          .attr('font-size', '10px')
          .attr('text-anchor', 'middle');
      });
  };

  // Dots - Bottom 1/3
  const dots = (selection, data) => {
    const jitterHeight = segmentHeight * 0.5; // Adjust jitter height to fit within the segment
    const dotOffset = 20; // Additional offset to pull dots down
    const tooltip = d3.select("body")
      .append('div') // Append to body
      .attr('class', 'tooltip') // Add class for styling
      .style('position', 'absolute')
      .style('background', 'white')
      .style('border', '1px solid black')
      .style('padding', '5px')
      .style('border-radius', '5px')
      .style('opacity', 0)
      .style('pointer-events', 'none')
      .style('z-index', '1000'); // Ensure it's above other elements

    selection
      .append('g')
      .classed('dots', true)
      .attr('transform', `translate(0, ${segmentHeight * 2})`) // Position in the bottom segment
      .selectAll('circle')
      .data(data)
      .enter()
      .append('circle')
      .attr('r', 5)
      .attr('cx', (d) => x(d)) // Keep x-axis alignment consistent with boxplot and density
      .attr('cy', () => (Math.random() - 0.5) * jitterHeight + dotOffset) // Add random vertical jitter and offset
      .style('fill', 'grey')
      .style('opacity', 0.6)
      .attr('stroke', 'none')
      .on('mouseover', function (event, d) {
        console.log('Mouseover event:', event); // Debugging log
        console.log('Data point (d):', d); // Debugging log
        tooltip
          .style('opacity', 1)
          .style('visibility', 'visible')
          .html(`XP Score: ${Math.round(d)}`)
          .style('left', `${event.pageX + 10}px`)
          .style('top', `${event.pageY - 20}px`);
        d3.select(this).attr('stroke', 'black').attr('stroke-width', 1);
      })
      .on("mousemove", (event) => {
        tooltip
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 20}px`);
      })
      .on('mouseout', function () {
        tooltip.style('opacity', 0);
        d3.select(this).attr('stroke', 'none');
      });
  };

  // Call the raincloud rendering function
  svg.append('g').call(raincloud, sortedData);
}
