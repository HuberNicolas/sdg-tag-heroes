import { ref, onMounted } from 'vue';
import * as d3 from 'd3';
import LeaderLine from 'leader-line-new';
import { coords, sdgColors, sdgShortTitles } from '@/constants/constants';

export default function useConnect() {
  const fixedConnections = ref([]);
  const currentHex = ref(null);
  const hexRadius = 50;
  const arrowLines = ref([]); // Array to store all pre-created arrows

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
      .attr('transform', `translate(${width / 4}, ${height / 2})`);

    coords.forEach(([x, y], i) => {
      const color = d3.color(sdgColors[i % sdgColors.length]);
      const value = 1.0;
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
        .attr('data-id', sdgShortTitles[i])
        .attr('data-color', color?.toString())
        .text(sdgShortTitles[i])
        .style('font-size', '12px')
        .style('fill', 'black');
    });
  };

  const renderDecisionHex = (selector, width, height, color, label) => {
    const container = d3.select(selector);
    container.selectAll('*').remove();

    // complete svg
    const svg = container
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('transform', `translate(${width}, ${height*0})`)
      .style('background', 'transparent');

    // rendered hex inside
    const hexagonGroup = svg.append('g')
      .attr('transform', `translate(${width/2}, ${height/2})`);

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
      .style('font-size', '12px')
      .style('fill', 'black');
  };

  const initArrows = () => {
    const hexagons = document.querySelectorAll('.hexagon');
    const targetBox = document.getElementById('target-box');

    hexagons.forEach((hex) => {
      const hexColor = hex.getAttribute('data-color');
      const line = new LeaderLine(hex, targetBox, {
        color: hexColor || 'blue',
        startPlug: 'behind',
        endPlug: 'arrow1',
        dash: { animation: true },
        visible: false, // Hide arrows initially
      });
      arrowLines.value.push(line);
    });
  };

  const toggleArrow = (hex) => {
    const hexIndex = sdgShortTitles.indexOf(hex.getAttribute('data-id'));
    const line = arrowLines.value[hexIndex];

    if (!line) return;

    if (line.visible) {
      line.hide();
      line.visible = false;
      currentHex.value = null;
      renderDecisionHex('#target-box', 150, 150, 'whitesmoke', 'Publication');
    } else {
      arrowLines.value.forEach((arrow) => arrow.hide());
      line.show();
      line.visible = true;
      currentHex.value = hex;
      const hexColor = hex.getAttribute('data-color');
      renderDecisionHex('#target-box', 150, 150, hexColor, hex.getAttribute('data-id'));
    }
  };

  const initHoverAndClick = () => {
    const hexagons = document.querySelectorAll('.hexagon');

    hexagons.forEach((hex) => {
      hex.addEventListener('click', () => toggleArrow(hex));
    });
  };

  onMounted(() => {
    renderHexGrid('#glyph-container', 500, 500);
    renderDecisionHex('#target-box', 150, 150, 'whitesmoke', 'Publication');
    initArrows();
    initHoverAndClick();
  });

  return { fixedConnections };
}
