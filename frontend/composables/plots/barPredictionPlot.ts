import * as d3 from 'd3';
import { useSDGsStore } from '~/stores/sdgs';

export function createBarPlot(container: HTMLElement, values: number[], width: number, height: number) {
  if (!values || values.length !== 17) {
    console.error('Invalid values: must be an array of 17 numbers.');
    return;
  }

  const sdgsStore = useSDGsStore(); // Access the SDG store for colors

  // Extract the top 3 SDG predictions
  const top3Predictions = values
    .map((value, index) => ({
      key: `${index+1}`, // SDG number (e.g., "1", "2", "3")
      value,
      color: sdgsStore.getColorBySDG(index + 1) || '#CCCCCC', // Fetch color from the store or fallback to gray
    }))
    .sort((a, b) => b.value - a.value) // Sort by value descending
    .slice(0, 3); // Take the top 3 predictions

  // Set up margins
  const margin = { top: 0, right: 30, bottom: 0, left: 20 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;

  // Remove any previous SVG in the container
  d3.select(container).selectAll('*').remove();

  // Append the SVG object
  const svg = d3
    .select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // X-axis: Linear scale for prediction values
  const x = d3
    .scaleLinear()
    .domain([0, d3.max(top3Predictions, (d) => d.value) || 1])
    .range([0, plotWidth]);

  svg
    .append('g')
    .attr('transform', `translate(0,${plotHeight})`)
    .call(d3.axisBottom(x).ticks(5))
    .selectAll('text')
    .style('text-anchor', 'middle');

  // Y-axis: Band scale for SDG labels
  const y = d3
    .scaleBand()
    .domain(top3Predictions.map((d) => d.key)) // SDG numbers as labels
    .range([0, plotHeight])
    .padding(0.1);

  svg.append('g').call(d3.axisLeft(y));

  // Bars
  svg
    .selectAll('rect')
    .data(top3Predictions)
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', (d) => y(d.key) || 0)
    .attr('width', (d) => x(d.value))
    .attr('height', y.bandwidth())
    .attr('fill', (d) => d.color); // Use SDG-specific colors

  // Add labels to bars
  svg
    .selectAll('text.bar-label')
    .data(top3Predictions)
    .enter()
    .append('text')
    .attr('class', 'bar-label')
    .attr('x', (d) => x(d.value) + 5)
    .attr('y', (d) => (y(d.key) || 0) + y.bandwidth() / 2)
    .attr('dy', '.35em')
    .style('fill', '#000')
    .style('font-size', '12px')
    .text((d) => Math.floor(d.value * 100) / 100); // This will round down to two decimal places
}
