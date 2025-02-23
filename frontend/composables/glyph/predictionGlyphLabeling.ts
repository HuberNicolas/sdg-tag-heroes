import * as d3 from 'd3';
import {baseSdgTitles, baseSdgShortTitles, baseSdgColors, baseCoords, baseLabelsNumbers} from "@/constants/constants";
import {trimValue} from "~/utils/trim";
import {useSDGsStore} from "~/stores/sdgs";
import {useSDGPredictionsStore} from "~/stores/sdgPredictions";
import { storeToRefs } from "pinia";

export default function createGlyph() {
  const sdgsStore = useSDGsStore();
  const sdgPredictionsStore = useSDGPredictionsStore();
  const hexRadius = 30; // Hexagon radius in pixels

  const scaleFactor = 0.9; // Scaling factor to reduce spacing (less than 1 reduces spacing)

  // New spacing values based on the scale factor
  const xSpacing = hexRadius * 2 * scaleFactor; // Horizontal spacing
  const ySpacing = Math.sqrt(3) * hexRadius * scaleFactor; // Vertical spacing


  const coords = baseCoords
  const labels = baseLabelsNumbers
  const sdgTitles = baseSdgTitles
  const sdgShortTitles = baseSdgShortTitles
  const sdgColors = baseSdgColors

  // Fetch predictions based on publicationId
  const fetchPredictions = async (publicationId: number) => {
    try {
      const predictions = await sdgPredictionsStore.fetchDefaultModelSDGPredictionsByPublicationId(publicationId);
      const prediction = sdgPredictionsStore.getLabelingSDGPrediction
      if (prediction) {
        const values =  [
          prediction.sdg1, prediction.sdg2, prediction.sdg3, prediction.sdg4, prediction.sdg5,
          prediction.sdg6, prediction.sdg7, prediction.sdg8, prediction.sdg9, prediction.sdg10,
          prediction.sdg11, prediction.sdg12, prediction.sdg13, prediction.sdg14, prediction.sdg15,
          prediction.sdg16, prediction.sdg17
        ];
        return values;
      }
    } catch (error) {
      console.error("Failed to fetch SDG predictions:", error);
      return Array(17).fill(0); // Return default values in case of error
    }
  };


  const renderHexGrid = async (selector: HTMLElement, width: number = 100, height: number = 100, publicationId: number): void => {
    if (!publicationId) return;
    const { selectedSDG } = storeToRefs(sdgsStore);

    // Fetch predictions
    const values = await fetchPredictions(publicationId);

    const xCoords = coords.map(([x]) => x * xSpacing);
    const yCoords = coords.map(([_, y]) => y * ySpacing);

    // Calculate the bounds of the glyph content
    const minX = Math.min(...xCoords) - hexRadius;
    const maxX = Math.max(...xCoords) + hexRadius;
    const minY = Math.min(...yCoords) - hexRadius;
    const maxY = Math.max(...yCoords) + hexRadius;

    const gridWidth = maxX - minX; // Actual content width
    const gridHeight = maxY - minY; // Actual content height

    // Slight manual adjustments for centering
    const xShift = hexRadius; // Move slightly to the right
    const yShift = -hexRadius; // Move slightly up

    // Centering offsets with manual adjustments
    const xOffset = (width - gridWidth) / 2 + xShift;
    const yOffset = (height - gridHeight) / 2 + yShift;

    const container = d3.select(selector);
    container.selectAll('*').remove();

    const svg = container
      .append('svg')
      .attr('viewBox', `${minX} ${minY} ${gridWidth} ${gridHeight}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('width', width)
      .attr('height', height)
      .style('background', 'transparent');

    // Create a group to shift content
    const contentGroup = svg.append('g')
      //.attr('transform', `translate(${xOffset - minX}, ${yOffset - minY})`); // Apply explicit horizontal adjustment

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

    coords.forEach(([x, y], i) => {
      const color = d3.color(sdgColors[i % sdgColors.length]);
      const value = values[i];
      const innerRadius = (1 - value) * hexRadius;

      const hexagonGroup = contentGroup.append('g');

      const rotation = 30;

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
        .attr('stroke-width', selectedSDG.value === i + 1 ? 4 : 1)
        .attr('transform', `rotate(${rotation} ${x * xSpacing} ${y * ySpacing})`)


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
        //.attr('stroke', 'black')
        //.attr('stroke-width', 1)
        .attr('transform', `rotate(${rotation} ${x * xSpacing} ${y * ySpacing})`)

      hexagonGroup
        .append('text')
        .attr('x', x * xSpacing)
        .attr('y', y * ySpacing)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .text(sdgShortTitles[i])
        .style('font-size', '12px')
        .style('fill', 'black');

      hexagonGroup
        .on('mouseover', () => {
          tooltip
            .style('visibility', 'visible')
            .style('background', color?.toString() || 'gray')
            .style('color', '#fff')
            .html(`<strong>${sdgTitles[i]}</strong><br>Machine Score: ${trimValue(value)}`);
        })
        .on('mousemove', (event) => {
          tooltip
            .style('top', `${event.pageY + 10}px`)
            .style('left', `${event.pageX + 10}px`);
        })
        .on('mouseout', () => {
          tooltip.style('visibility', 'hidden');
        })
        // Click event moved to the entire hexagon group
        .on('click', (event) => {
        event.stopPropagation(); // Prevent interference with tooltip
          // Hide tooltip immediately on click
        tooltip.style('visibility', 'hidden');
        if (selectedSDG.value === i + 1) {
          sdgsStore.setSelectedSDG(0); // Deselect if already selected
        } else {
          sdgsStore.setSelectedSDG(i + 1); // Select the SDG
        }
        renderHexGrid(selector, width, height, publicationId); // Re-render to update stroke width
      });


    });
  };
  return { renderHexGrid };
}
