import { onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import * as d3 from 'd3';
import { baseCoords, baseSdgColors, baseSdgShortTitles, sdgNullColor, sdgNullCoord, sdgNullShortTitle } from '@/constants/constants';
import { useSDGsStore } from "@/stores/sdgs";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";

/*
 * "Identify" panel of the labeling page: a honeycomb of the 17 SDGs plus "Not relevant" and the
 * publication as a target hexagon. Each cell fills up with the community votes for that SDG.
 * Clicking a cell picks it as your label (sdgsStore.selectedSDGLabel: 1–17, -1 for not relevant,
 * 0 for none) and draws a connector from the cell to the publication.
 *
 * Everything is one SVG (the connector used to be a leader-line overlay fixed to the page, which
 * floated over other panels while scrolling). The drawing follows the store, so it also resets after
 * a label was submitted.
 */
export default function useConnect(containerSelector = '#glyph-container') {
  const sdgsStore = useSDGsStore();
  const labelDecisionsStore = useLabelDecisionsStore();

  const coords = [...baseCoords, sdgNullCoord];
  const sdgColors = [...baseSdgColors, sdgNullColor];
  const sdgShortTitles = [...baseSdgShortTitles, sdgNullShortTitle];

  const hexRadius = 30;
  const xSpacing = hexRadius * 2 * 0.9;
  const ySpacing = Math.sqrt(3) * hexRadius * 0.9;
  const maxVotesForScaling = 9; // 9 votes fill a cell completely

  // Store value of a cell: 1–17 for the SDGs, -1 for the last cell ("Not relevant")
  const labelOfIndex = (i: number) => (i >= 0 && i < 17 ? i + 1 : -1);
  const indexOfLabel = (label: number) => (label === -1 ? 17 : label >= 1 && label <= 17 ? label - 1 : null);

  // Pointy-top hexagons (like the other SDG glyphs), so the rows of the honeycomb interlock
  const hexPoints = (cx: number, cy: number, r: number) =>
    d3.range(6)
      .map((k) => {
        const angle = (Math.PI / 3) * k + Math.PI / 6;
        return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)].join(',');
      })
      .join(' ');

  const render = () => {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    const root = d3.select(container);
    root.selectAll('*').remove();

    // Layout in SVG units: honeycomb on the left, target hexagon on the right
    const cells = coords.map(([x, y], i) => ({ i, x: x * xSpacing, y: y * ySpacing }));
    const minX = d3.min(cells, (c) => c.x)! - hexRadius - 6;
    const maxX = d3.max(cells, (c) => c.x)! + hexRadius;
    const minY = d3.min(cells, (c) => c.y)! - hexRadius - 6;
    const maxY = d3.max(cells, (c) => c.y)! + hexRadius + 6;
    const target = { x: maxX + 150, y: (minY + maxY) / 2, r: 40 };
    const width = target.x + target.r + 20 - minX;
    const height = maxY - minY;

    const svg = root
      .append('svg')
      .attr('class', 'identify')
      .attr('viewBox', `${minX} ${minY} ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('role', 'radiogroup')
      .attr('aria-label', 'Pick the SDG of this publication');

    const selectedIndex = indexOfLabel(sdgsStore.getSelectedSDGLabel);

    // Votes per SDG
    const labelCounts = labelDecisionsStore.userLabels.reduce((acc, label) => {
      if ((label.votedLabel >= 1 && label.votedLabel <= 17) || label.votedLabel === -1) {
        acc[label.votedLabel] = (acc[label.votedLabel] || 0) + 1;
      }
      return acc;
    }, {} as Record<number, number>);

    // Connector (below the cells)
    const gLink = svg.append('g').attr('class', 'identify__link');

    const gCells = svg.append('g');
    cells.forEach(({ i, x, y }) => {
      const label = labelOfIndex(i);
      const votes = labelCounts[label] || 0;
      const fillingLevel = Math.min(0.1 + 0.9 * (votes / maxVotesForScaling), 1);
      const color = sdgColors[i];
      const isSelected = selectedIndex === i;

      const g = gCells
        .append('g')
        .attr('class', 'identify__cell')
        .classed('is-selected', isSelected)
        .classed('is-dim', selectedIndex !== null && !isSelected)
        .attr('role', 'radio')
        .attr('aria-checked', String(isSelected))
        .attr('tabindex', 0)
        .attr('aria-label', `${sdgShortTitles[i]}: ${votes} community votes`)
        .style('--cell', color)
        .on('click', () => toggle(i))
        .on('keydown', (event: KeyboardEvent) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggle(i);
          }
        });

      g.append('title').text(`${label === -1 ? 'Not relevant' : `SDG ${label}`} · ${sdgShortTitles[i]} · ${votes} vote${votes === 1 ? '' : 's'}`);
      // Outline cell, then the community fill growing from the centre
      g.append('polygon').attr('class', 'identify__shell').attr('points', hexPoints(x, y, hexRadius - 1.5));
      g.append('polygon').attr('class', 'identify__fill').attr('points', hexPoints(x, y, (hexRadius - 3) * fillingLevel));
      g.append('text')
        .attr('class', 'identify__label')
        .attr('x', x)
        .attr('y', y)
        .attr('dy', '0.35em')
        .text(sdgShortTitles[i]);
      if (votes > 0) {
        g.append('text')
          .attr('class', 'identify__votes')
          .attr('x', x)
          .attr('y', y + hexRadius * 0.55)
          .text(votes);
      }
    });

    // Target: the publication, coloured with your pick
    const pickedColor = selectedIndex !== null ? sdgColors[selectedIndex] : null;
    const gTarget = svg.append('g').attr('class', 'identify__target').classed('is-set', pickedColor !== null);
    gTarget.append('polygon').attr('class', 'identify__target-halo').attr('points', hexPoints(target.x, target.y, target.r + 10));
    gTarget
      .append('polygon')
      .attr('class', 'identify__target-hex')
      .attr('points', hexPoints(target.x, target.y, target.r))
      .style('fill', pickedColor ?? null);
    gTarget
      .append('text')
      .attr('class', 'identify__target-kicker')
      .attr('x', target.x)
      .attr('y', target.y - target.r - 18)
      .text(pickedColor ? '// your label' : '// your time to shine');
    gTarget
      .append('text')
      .attr('class', 'identify__target-label')
      .attr('x', target.x)
      .attr('y', target.y)
      .attr('dy', '0.35em')
      .text(selectedIndex !== null ? sdgShortTitles[selectedIndex] : 'Publication');

    if (selectedIndex !== null) {
      const from = cells[selectedIndex];
      const start: [number, number] = [from.x + hexRadius * 0.6, from.y];
      const end: [number, number] = [target.x - target.r - 4, target.y];
      const midX = (start[0] + end[0]) / 2;
      const d = `M${start[0]},${start[1]} C${midX},${start[1]} ${midX},${end[1]} ${end[0]},${end[1]}`;
      gLink.append('path').attr('class', 'identify__wire-glow').attr('d', d).style('stroke', pickedColor);
      gLink.append('path').attr('class', 'identify__wire').attr('d', d).style('stroke', pickedColor);
      gLink.append('circle').attr('class', 'identify__wire-end').attr('cx', end[0]).attr('cy', end[1]).attr('r', 3.5).style('fill', pickedColor);
    }
  };

  const toggle = (i: number) => {
    const label = labelOfIndex(i);
    sdgsStore.setSelectedSDGLabel(sdgsStore.getSelectedSDGLabel === label ? 0 : label);
  };

  // Redraw when the votes or the pick change
  const stopVotes = watch(
    () => labelDecisionsStore.userLabels,
    async () => {
      await nextTick();
      render();
    },
    { deep: true },
  );
  const stopPick = watch(() => sdgsStore.getSelectedSDGLabel, render);

  onMounted(render);
  onBeforeUnmount(() => {
    stopVotes();
    stopPick();
  });

  return {};
}
