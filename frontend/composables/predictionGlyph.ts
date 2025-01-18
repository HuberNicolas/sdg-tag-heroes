import * as d3 from 'd3';
import {sdgTitles, sdgColors} from "@/constants/constants";

export default function createGlyph(values: number[]) {
  const hexRadius = 50; // Hexagon radius in pixels

  const scaleFactor = 0.9; // Scaling factor to reduce spacing (less than 1 reduces spacing)

  // New spacing values based on the scale factor
  const xSpacing = hexRadius * 2 * scaleFactor; // Horizontal spacing
  const ySpacing = Math.sqrt(3) * hexRadius * scaleFactor; // Vertical spacing

  const coords = [
    [0, -2], [1, -2], [2, -2],
    [-0.5, -1], [0.5, -1], [1.5, -1], [2.5, -1],
    [0, 0], [1, 0], [2, 0],
    [-0.5, 1], [0.5, 1], [1.5, 1], [2.5, 1],
    [0, 2], [1, 2], [2, 2],
  ];

  const labels = [
    '1', '2', '3',
    '4', '5', '6', '7',
    '8', '9', '10', '11',
    '12', '13', '14',
    '15', '16', '17',
  ];

  const renderHexGrid = (selector: HTMLElement): void => {
    const gridWidth = (Math.max(...coords.map(([x]) => x)) + 3) * xSpacing;
    const gridHeight = (Math.max(...coords.map(([_, y]) => y)) + 3) * ySpacing;

    const container = d3.select(selector);
    container.selectAll('*').remove();

    const svg = container
      .append('svg')
      .attr('viewBox', `-${xSpacing} ${-0.623 * gridHeight} ${gridWidth} ${gridHeight + ySpacing}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('width', '100%')
      .attr('height', '100%')
      .style('background', 'transparent')


    const tooltip = d3.select('body') // Append tooltip to the body
      .append('div')
      .attr('class', 'glyph-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background', '#fff')
      .style('border', '1px solid #ccc')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('box-shadow', '0px 4px 8px rgba(0, 0, 0, 0.1)')
      .style('z-index', '1000'); // Ensure it appears above other content


    coords.forEach(([x, y], i) => {
      const color = d3.color(sdgColors[i % sdgColors.length]);
      const value = values[i];
      const innerRadius = (1-value) * hexRadius;

      const hexagonGroup = svg.append('g');

      const rotation = 30;

      // Outer hexagon
      hexagonGroup
        .append('polygon')
        .attr(
          'points',
          d3.range(6)
            .map((k) => {
              const angle = Math.PI / 3 * k;
              return [
                x * xSpacing + hexRadius * Math.cos(angle),
                y * ySpacing + hexRadius * Math.sin(angle),
              ].join(',');
            })
            .join(' ')
        )
        .attr('fill', color?.toString() || 'gray')
        .attr('stroke', 'black')
        .attr('stroke-width', 1)
        .attr('transform', `rotate(${rotation} ${x * xSpacing} ${y * ySpacing})`);

      // Inner hexagon
      hexagonGroup
        .append('polygon')
        .attr(
          'points',
          d3.range(6)
            .map((k) => {
              const angle = Math.PI / 3 * k;
              return [
                x * xSpacing + innerRadius * Math.cos(angle),
                y * ySpacing + innerRadius * Math.sin(angle),
              ].join(',');
            })
            .join(' ')
        )
        .attr('fill', 'white')
        .attr('stroke', 'black')
        .attr('stroke-width', 1)
        .attr('transform', `rotate(${rotation} ${x * xSpacing} ${y * ySpacing})`);

      // Add label
      hexagonGroup
        .append('text')
        .attr('x', x * xSpacing)
        .attr('y', y * ySpacing)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .text(labels[i])
        .style('font-size', '12px')
        .style('fill', 'black');

      // Tooltip events
      hexagonGroup
        .on('mouseover', () => {
          tooltip
            .style('visibility', 'visible')
            .style('background', color?.toString() || 'gray') // Use SDG color as background
            .style('color', '#fff') // Make text white for contrast
            .html(`<strong>${sdgTitles[i]}</strong><br>Value: ${value.toFixed(2)}`);
          console.log("Hello")
        })
        .on('mousemove', (event) => {
          tooltip
            .style('top', `${event.pageY + 10}px`) // Add offset to avoid cursor overlap
            .style('left', `${event.pageX + 10}px`);
          console.log("Hello")
        })
        .on('mouseout', () => {
          tooltip.style('visibility', 'hidden');
          console.log("Hello")
        });


    });
  };

  return { renderHexGrid };
}
