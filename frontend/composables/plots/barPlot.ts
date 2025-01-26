import Plotly from 'plotly.js-dist';
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useSDGsStore } from "~/stores/sdgs";

export function createBarPlot(container, width, height) {
  const sdgPredictionsStore = useSDGPredictionsStore();
  const sdgsStore = useSDGsStore();

  // Watch for changes in the selected SDG predictions
  sdgPredictionsStore.$subscribe((mutation, state) => {
    if (state.selectedPartitionedSDGPredictions.length > 0) {
      const sdgDistribution = aggregateSDGPredictions(state.selectedPartitionedSDGPredictions);
      updateBarPlot(container, sdgDistribution, width, height, sdgsStore);
    }
  });

  // Initial render (optional)
  if (sdgPredictionsStore.selectedPartitionedSDGPredictions.length > 0) {
    const sdgDistribution = aggregateSDGPredictions(sdgPredictionsStore.selectedPartitionedSDGPredictions);
    updateBarPlot(container, sdgDistribution, width, height, sdgsStore);
  }
}

function aggregateSDGPredictions(sdgPredictions) {
  const sdgCounts = new Array(17).fill(0);

  sdgPredictions.forEach(prediction => {
    if (prediction) {
      // Find the max SDG prediction dynamically
      const maxSDG = Object.entries(prediction)
        .filter(([key]) => key.startsWith('sdg')) // Only include SDG keys
        .reduce((max, [key, value]) => {
          return value > max.value ? { key, value } : max;
        }, { key: null, value: -Infinity });

      if (maxSDG.key) {
        // Extract the SDG number from the key
        const sdgId = parseInt(maxSDG.key.replace('sdg', ''), 10);
        if (sdgId >= 1 && sdgId <= 17) {
          sdgCounts[sdgId - 1]++; // Increment the count for the corresponding SDG
        }
      }
    }
  });

  return sdgCounts;
}

function updateBarPlot(container, sdgDistribution, width, height, sdgsStore) {
  const sdgLabels = Array.from({ length: 17 }, (_, i) => `SDG ${i + 1}`);
  const colors = sdgLabels.map((_, index) => sdgsStore.getColorBySDG(index + 1) || '#CCCCCC'); // Fallback color if no color is found

  const data = [{
    x: sdgLabels,
    y: sdgDistribution,
    type: 'bar',
    marker: {
      color: colors,
    },
  }];

  const layout = {
    title: 'SDG Distribution for Selected Points',
    barmode: 'group',
    width: width,
    height: height,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: {
      showgrid: false,
      zeroline: false,
    },
    yaxis: {
      showgrid: true,
      zeroline: false,
    },
  };

  Plotly.newPlot(container, data, layout);
}
