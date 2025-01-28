import * as d3 from 'd3';
import {baseSdgColors, baseCoords, baseLabelsNumbers} from "@/constants/constants";



export default function createGlyph(values: number[]) {
  const hexRadius = 50; // Hexagon radius in pixels
  const scaleFactor = 0.9; // Scaling factor to reduce spacing (less than 1 reduces spacing)
  const xSpacing = hexRadius * 2 * scaleFactor; // Horizontal spacing
  const ySpacing = Math.sqrt(3) * hexRadius * scaleFactor; // Vertical spacing

  const sdgColors = baseSdgColors;
  const coords = baseCoords
  const labels = baseLabelsNumbers



  const renderHexGrid = (selector: HTMLElement, width: number, height: number): void => {
    const xCoords = coords.map(([x]) => x * xSpacing);
    const yCoords = coords.map(([_, y]) => y * ySpacing);

    const minX = Math.min(...xCoords) - hexRadius;
    const maxX = Math.max(...xCoords) + hexRadius;
    const minY = Math.min(...yCoords) - hexRadius;
    const maxY = Math.max(...yCoords) + hexRadius;

    const gridWidth = maxX - minX;
    const gridHeight = maxY - minY;

    const container = d3.select(selector);
    container.selectAll('*').remove();

    const svg = container
      .append('svg')
      .attr('viewBox', `${minX} ${minY} ${gridWidth} ${gridHeight}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('width', width)
      .attr('height', height)
      .style('background', 'transparent');

    const contentGroup = svg.append('g');

    const tooltip = d3.select('body')
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
      .style('z-index', '1000');

    let selectedHexagon: d3.Selection<SVGPolygonElement, unknown, null, undefined> | null = null;
    const sdgsStore = useSDGsStore();

    coords.forEach(([x, y], i) => {
      const color = d3.color(sdgColors[i % sdgColors.length]);
      const value = values[i];
      const innerRadius = (1 - value) * hexRadius;

      const hexagonGroup = contentGroup.append('g');

      const rotation = 30;

      const hexagon = hexagonGroup
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

      hexagonGroup
        .append('text')
        .attr('x', x * xSpacing)
        .attr('y', y * ySpacing)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .text(labels[i])
        .style('font-size', '12px')
        .style('fill', 'black');

      hexagonGroup
        .on('mouseover', () => {
          tooltip
            .style('visibility', 'visible')
            .style('background', color?.toString() || 'gray')
            .style('color', '#fff')
            .html(`<strong>${sdgTitles[i]}</strong><br>Value: ${value.toFixed(2)}`);
        })
        .on('mousemove', (event) => {
          tooltip
            .style('top', `${event.pageY + 10}px`)
            .style('left', `${event.pageX + 10}px`);
        })
        .on('mouseout', () => {
          tooltip.style('visibility', 'hidden');
        })
        .on('click', () => {
          if (selectedHexagon === hexagon) {
            // Deselect if already selected
            selectedHexagon.attr('stroke', 'black').attr('stroke-width', 1);
            selectedHexagon = null;
            sdgsStore.setSelectedSDG(null);
          } else {
            // Deselect previous selection
            if (selectedHexagon) {
              selectedHexagon.attr('stroke', 'black').attr('stroke-width', 1);
            }
            // Select the new hexagon
            selectedHexagon = hexagon;
            hexagon.attr('stroke', 'black').attr('stroke-width', 3);
            sdgsStore.setSelectedSDG(i+1);
          }
        });
    });
  };

  return { renderHexGrid };
}
