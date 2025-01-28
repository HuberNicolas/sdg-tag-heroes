import Plotly from 'plotly.js-dist';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";

export function createBarLabelPlot(container, width, height) {
  const labelDecisionsStore = useLabelDecisionsStore();
  const sdgsStore = useSDGsStore();

  // Watch for changes in the selected SDG label decision and user labels
  labelDecisionsStore.$subscribe((mutation, state) => {
    if (state.selectedSDGLabelDecision && state.userLabels) {
      const labelDistribution = aggregateUserVotes(state.userLabels);
      updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore);
    }
  });

  // Initial render
  if (labelDecisionsStore.selectedSDGLabelDecision && labelDecisionsStore.userLabels) {
    const labelDistribution = aggregateUserVotes(labelDecisionsStore.userLabels);
    updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore);
  }
}

function aggregateUserVotes(userLabels) {
  const voteCounts = {};

  userLabels.forEach(label => {
    const votedLabel = label.votedLabel;
    if ((votedLabel >= 1 && votedLabel <= 17) || votedLabel === -1) {
      voteCounts[votedLabel] = (voteCounts[votedLabel] || 0) + 1;
    }
  });

  return voteCounts;
}

function updateLabelDistributionBarPlot(container, labelDistribution, width, height, sdgsStore) {
  const labels = Object.keys(labelDistribution).map(Number);
  const counts = Object.values(labelDistribution);

  const sortedIndices = counts
    .map((count, index) => ({ count, index }))
    .sort((a, b) => b.count - a.count)
    .map(({ index }) => index);

  const sortedLabels = sortedIndices.map(i => labels[i]);
  const sortedCounts = sortedIndices.map(i => counts[i]);

  const colors = sortedLabels.map(label => {
    if (label === -1) return '#000000';
    if (label >= 1 && label <= 17) return sdgsStore.getColorBySDG(label) || '#CCCCCC';
    return '#CCCCCC';
  });

  const filteredLabels = sortedLabels.filter((_, i) => sortedCounts[i] > 0);
  const filteredCounts = sortedCounts.filter(count => count > 0);
  const filteredColors = colors.filter((_, i) => sortedCounts[i] > 0);

  const data = [{
    x: filteredLabels.map(label => (label === -1 ? 'Undefined' : `SDG ${label}`)),
    y: filteredCounts,
    type: 'bar',
    marker: { color: filteredColors },
  }];

  const layout = {
    barmode: 'group',
    width,
    height,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: { showgrid: false, zeroline: false, title: '' },
    yaxis: { showgrid: true, zeroline: false, title: '' },
  };

  Plotly.newPlot(container, data, layout);
}
