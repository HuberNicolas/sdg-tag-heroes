import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as d3 from 'd3';
import LeaderLine from 'leader-line-new';
import { baseCoords, baseSdgColors, baseSdgShortTitles, sdgNullColor, sdgNullCoord, sdgNullShortTitle } from '@/constants/constants';
import { useSDGsStore } from "@/stores/sdgs";
import {useLabelDecisionsStore} from "~/stores/sdgLabelDecisions";

export default function useConnect() {
  const sdgsStore = useSDGsStore();  // Initialize the store
  const labelDecisionsStore = useLabelDecisionsStore();

  const fixedConnections = ref([]);
  const currentHex = ref(null);
  const hexRadius = 30;
  const arrowLines = ref([]); // Array to store all pre-created arrows

  const coords = [...baseCoords, sdgNullCoord];
  const sdgColors = [...baseSdgColors, sdgNullColor];
  const sdgShortTitles = [...baseSdgShortTitles, sdgNullShortTitle];

  watch(
    () => labelDecisionsStore.userLabels,
    async (newLabels) => {
      if (newLabels.length > 0) {
        console.log("User labels are ready, redrawing hex grid...");

        await nextTick(); // Ensures DOM updates before rendering

        renderHexGrid("#glyph-container", 260, 260);

        await nextTick(); // Ensure hexagons are present before binding events
        initHoverAndClick();
      }
    },
    { deep: true, immediate: true } // Immediate ensures it runs if `userLabels` is already set
  );



  // Move cleanup functions to the top
  const cleanupLeaderLines = () => {
    arrowLines.value.forEach(line => {
      safeRemoveLine(line);
    });
    arrowLines.value = [];
  };

  const safeRemoveLine = (line) => {
    try {
      line.remove();
    } catch (error) {
      console.warn('Failed to remove LeaderLine:', error);
    }
  };

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
      .attr('transform', `translate(${width / 4}, ${height / 2})`);  // Adjusted to position on the left

    // Count occurrences of each votedLabel once instead of inside the loop
    const labelCounts = labelDecisionsStore.userLabels.reduce((acc, label) => {
      if (label.votedLabel >= 1 && label.votedLabel <= 17) {
        acc[label.votedLabel] = (acc[label.votedLabel] || 0) + 1;
      }
      return acc;
    }, {});

    const maxVotes = Math.max(...Object.values(labelCounts), 1);
    const minVotes = 0;
    const maxVotesForScaling = 9; // 10 votes correspond to 100% filling

    coords.forEach(([x, y], i) => {
      const sdgId = i + 1; // SDG IDs are 1-based
      const votes = labelCounts[sdgId] || 0;
      const voteRatio = votes / maxVotesForScaling; // Calculate ratio of votes

      // Filling level scaling
      const minFilling = 0.1; // 10% filling for 0 votes
      const maxFilling = 1.0; // 100% filling for 10 votes
      const fillingLevel = Math.min(minFilling + (maxFilling - minFilling) * voteRatio, maxFilling);

      //console.log(`SDG ${sdgId}: ${votes} votes, filling level: ${fillingLevel.toFixed(2)}`);

      const color = d3.color(sdgColors[i % sdgColors.length]); // Keep the same color
      const fillColor = color.toString(); // Use the full color for the outer hexagon

      const hexagonGroup = contentGroup.append('g');
      const rotation = 30;

      // Outer hexagon (full color)
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
        .attr('fill', fillColor)
        .attr('stroke', 'black')
        .attr('stroke-width', 1)
        .attr('transform', `rotate(${rotation} ${x * xSpacing} ${y * ySpacing})`);

      // Inner hexagon (white with adjusted radius based on filling level)
      const innerRadius = hexRadius * (1-fillingLevel);

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

      // Text label
      contentGroup
        .append('text')
        .attr('x', x * xSpacing)
        .attr('y', y * ySpacing)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('class', 'hexagon')
        .attr('data-color', color?.toString())
        .attr('data-id', sdgShortTitles[i])
        .text(sdgShortTitles[i])
        .style('font-size', '8px')
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

    // Keep the decision hexagon **centered properly**
    const hexagonGroup = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    const rotation = 30;

    hexagonGroup
      .append('polygon')
      .attr(
        'points',
        d3.range(6).map((k) => {
          const angle = Math.PI / 3 * k;
          return [
            hexRadius * Math.cos(angle),
            hexRadius * Math.sin(angle),
          ].join(',');
        }).join(' ')
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
      .style('font-size', '8px')
      .style('fill', 'black');
  };

  const initArrows = () => {
    arrowLines.value = []; // Clear existing arrows

    const hexagons = document.querySelectorAll('.hexagon');
    const targetHex = document.querySelector('#target-box svg g');  // Select the entire group (G) instead of just the polygon

    hexagons.forEach((hex) => {
      const hexIndex = sdgShortTitles.indexOf(hex.getAttribute('data-id')); // Get SDG index
      if (hexIndex === -1) return; // Skip if not found

      const hexColor = hex.getAttribute('data-color');

      const line = new LeaderLine(
        LeaderLine.pointAnchor(hex, { x: '50%', y: '200%' }), // Start at hexagon center
        LeaderLine.pointAnchor(targetHex, { x: '50%', y: '50%' }), // End at decision hexagon center
        {
          color: hexColor || 'blue',
          startPlug: 'behind',
          endPlug: 'arrow1',
          dash: { animation: true },
          //path: 'straight',  // Ensures a clean and structured arrow path
          size: 2,  // Small and cleaner arrows
          startSocket: 'right', // Align arrows from right side of hex
          endSocket: 'left', // Align arrows to left side of decision hex
          visibility: 'hidden',
        }
      );
      arrowLines.value[hexIndex] = line; // Store the arrow in the correct index
      arrowLines.value.push(line);
    });
  };



  const toggleArrow = (hex) => {
    const hexIndex = sdgShortTitles.indexOf(hex.getAttribute('data-id'));
    const line = arrowLines.value[hexIndex];

    if (!line) return;

    const sdgId = (hexIndex >= 0 && hexIndex < 17) ? hexIndex + 1 : -1;

    if (line.visible) {
      line.hide();
      line.visible = false;
      sdgsStore.setSelectedSDGLabel(0);
      currentHex.value = null;
      renderDecisionHex('#target-box', 60, 60, 'whitesmoke', 'Publication');
    } else {
      arrowLines.value.forEach((arrow) => arrow.hide());
      line.show();
      line.visible = true;
      sdgsStore.setSelectedSDGLabel(sdgId);
      currentHex.value = hex;
      const hexColor = hex.getAttribute('data-color');
      renderDecisionHex('#target-box', 60, 60, hexColor, hex.getAttribute('data-id'));
    }
  };

  const initHoverAndClick = () => {
    const hexagons = document.querySelectorAll('.hexagon');
    hexagons.forEach((hex) => {
      hex.addEventListener('click', () => toggleArrow(hex));
    });
  };

  // Add cleanup listeners
  onUnmounted(() => {
    cleanupLeaderLines();
  });

  window.addEventListener('beforeunload', cleanupLeaderLines);

  onMounted(async () => {
    renderHexGrid('#glyph-container', 260, 260);
    renderDecisionHex('#target-box', 60, 60, 'whitesmoke', 'Publication');
    initArrows();
    await nextTick();
    initHoverAndClick();
  });

  return { fixedConnections };
}
