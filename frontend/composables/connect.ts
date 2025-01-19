import { ref, onMounted } from 'vue';
import * as d3 from 'd3';
import LeaderLine from 'leader-line-new';
import { sdgTitles, sdgColors } from '@/constants/constants';

export default function useConnect() {
  const fixedConnections = ref([]);
  const activeLine = ref(null);
  const currentHex = ref(null);
  const hexRadius = 50;
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

  const renderHexGrid = (selector, width, height) => {
    const xSpacing = hexRadius * 2 * 0.9;
    const ySpacing = Math.sqrt(3) * hexRadius * 0.9;

    const container = d3.select(selector);
    container.selectAll('*').remove();

    const svg = container
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .style('background', 'transparent');

    const contentGroup = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    coords.forEach(([x, y], i) => {

      const color = d3.color(sdgColors[i % sdgColors.length]);
      const value = 0.5;
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
      contentGroup
        .append('text')
        .attr('x', x * xSpacing)
        .attr('y', y * ySpacing)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('class', 'hexagon')
        .attr('data-id', labels[i])
        .attr('data-color', color?.toString())
        .text(labels[i])
        .style('font-size', '12px')
        .style('fill', 'black');
    });
  };

  const renderDecisionHex = (selector, width, height, color, label) => {
    const container = d3.select(selector);
    container.selectAll('*').remove();

    const svg = container
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .style('background', 'transparent');

    const hexagonGroup = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    const rotation = 30;

    hexagonGroup
      .append('polygon')
      .attr(
        'points',
        d3.range(6)
          .map((k) => {
            const angle = Math.PI / 3 * k;
            return [
              hexRadius * Math.cos(angle),
              hexRadius * Math.sin(angle),
            ].join(',');
          })
          .join(' ')
      )
      .attr('fill', color)
      .attr('stroke', 'black')
      .attr('stroke-width', 1)
      .attr('transform', `rotate(${rotation} 0 0)`);

    hexagonGroup
      .append('text')
      .attr('x', 0)
      .attr('y', 0)
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .text(label)
      .style('font-size', '16px')
      .style('fill', 'black');
  };

  const initHoverAndClick = () => {
    const hexagons = document.querySelectorAll('.hexagon');
    const targetBox = document.getElementById('target-box');

    hexagons.forEach((hex) => {
      hex.addEventListener('mouseenter', () => {
        if (activeLine.value) {
          activeLine.value.remove();
        }
        const hexColor = hex.getAttribute('data-color');
        activeLine.value = new LeaderLine(hex, targetBox, {
          color: hexColor || 'blue',
          startPlug: 'behind',
          endPlug: 'arrow1',
          dash:  {animation: true},
          animation: { duration: 500, timing: 'ease-in-out' },
        });
      });

      hex.addEventListener('mouseleave', () => {
        if (activeLine.value) {
          activeLine.value.remove();
          activeLine.value = null;
        }
      });

      hex.addEventListener('click', () => {
        if (currentHex.value === hex) {
          // Remove the existing line if clicked again
          if (activeLine.value) {
            activeLine.value.remove();
            activeLine.value = null;
            currentHex.value = null;
            renderDecisionHex('#target-box', 150, 150, 'whitesmoke', 'Publication');
          }
        } else {
          // Deselect the previous hexagon and remove its line
          if (currentHex.value && activeLine.value) {
            activeLine.value.remove();
          }

          // Select the new hexagon
          currentHex.value = hex;
          const hexColor = hex.getAttribute('data-color');
          activeLine.value = new LeaderLine(hex, targetBox, {
            color: hexColor || 'black',
            startPlug: 'behind',
            endPlug: 'arrow1',
            dash: true,
            animation: { duration: 500, timing: 'ease-in-out' },
          });
          renderDecisionHex('#target-box', 150, 150, hexColor, hex.getAttribute('data-id'));
        }
      });
    });
  };

  onMounted(() => {
    renderHexGrid('#glyph-container', 500, 500);
    renderDecisionHex('#target-box', 150, 150, 'whitesmoke', 'Publication');
    initHoverAndClick();
  });

  return { fixedConnections };
}
