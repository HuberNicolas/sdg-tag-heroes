import * as d3 from 'd3';

export default function useHexGrid(values: number[]) {
  const hexRadius = 50; // Hexagon radius in pixels
  const xSpacing = hexRadius * 2; // Horizontal spacing
  const ySpacing = Math.sqrt(3) * hexRadius; // Vertical spacing

  // Updated coordinate system
  const coords = [
    [0, 2], [1, 2], [2, 2],              // Row 1
    [-0.5, 1], [0.5, 1], [1.5, 1], [2.5, 1],  // Row 2
    [0, 0], [1, 0], [2, 0],              // Row 3
    [-0.5, -1], [0.5, -1], [1.5, -1], [2.5, -1], // Row 4
    [0, -2], [1, -2], [2, -2]            // Row 5
  ];

  const labels = [
    '1', '2', '3',
    '4', '5', '6', '7',
    '8', '9', '10', '11',
    '12', '13', '14',
    '15', '16', '17',
  ];

  const sdgColors = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C5192D', '#FF3A21',
    '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367',
    '#FD9D24', '#BF8B2E', '#3F7E44', '#0A97D9', '#56C02B',
    '#00689D', '#19486A',
  ];

  /**
   * Renders the hexagonal grid using D3.
   * @param selector - The CSS selector of the container element.
   */
  const renderHexGrid = (selector: HTMLElement): void => {
    // Calculate full grid dimensions
    const gridWidth = (Math.max(...coords.map(([x]) => x)) + 1.5) * xSpacing;
    const gridHeight = (Math.max(...coords.map(([_, y]) => y)) + 2) * ySpacing;

    const container = d3.select(selector);

    // Clear previous render
    container.selectAll('*').remove();

    // Add SVG with proper scaling
    const svg = container
      .append('svg')
      .attr('viewBox', `-${xSpacing} ${-0.623*gridHeight} ${gridWidth} ${gridHeight + ySpacing}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('width', '100%')
      .attr('height', '100%')
      .style('background', 'white');

    coords.forEach(([x, y], i) => {
      const color = d3.color(sdgColors[i % sdgColors.length]);
      const value = values[i];
      const innerRadius = value * hexRadius;

      // Outer hexagon
      svg
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
        .attr('stroke-width', 1);

      // Inner hexagon
      svg
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
        .attr('stroke-width', 1);

      // Add label
      svg
        .append('text')
        .attr('x', x * xSpacing)
        .attr('y', y * ySpacing)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .text(labels[i])
        .style('font-size', '12px')
        .style('fill', 'black');
    });
  };

  return { renderHexGrid };
}
