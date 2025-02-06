import Plotly from 'plotly.js-dist';
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useGameStore } from "~/stores/game";
import { useSDGsStore} from "~/stores/sdgs";

export function createScatterPlot(container, width, height, mode = 'top1') {
  const dimensionalityReductionsStore = useDimensionalityReductionsStore();
  const publicationsStore = usePublicationsStore();
  const sdgPredictionsStore = useSDGPredictionsStore();
  const labelDecisionsStore = useLabelDecisionsStore();
  const gameStore = useGameStore();
  const sdgsStore = useSDGsStore();

  const level = gameStore.getLevel;
  const sdg = gameStore.getSDG;

  // Fetch partitioned data from all stores
  const fetchData = async () => {
    const reductionShorthand = 'UMAP-15-0.0-2';

    await Promise.all([
      dimensionalityReductionsStore.fetchDimensionalityReductionsBySDGAndLevel(sdg, reductionShorthand, level),
      publicationsStore.fetchPublicationsForDimensionalityReductions(sdg, reductionShorthand, level),
      sdgPredictionsStore.fetchSDGPredictionsByLevel(sdg, reductionShorthand, level),
      sdgsStore.fetchSDGs(),
      labelDecisionsStore.fetchSDGLabelDecisionsForReduction(sdg, reductionShorthand, level),
  ]);
  }

  fetchData().then(() => {
    const dimensionalityReductionsData = dimensionalityReductionsStore.sdgLevelReductions;
    const publicationsData = publicationsStore.sdgLevelPublications;
    const sdgPredictionsData = sdgPredictionsStore.sdgLevelSDGPredictions;

    console.log(dimensionalityReductionsData);
    console.log(publicationsData);
    console.log(sdgPredictionsData);

    const combinedData = dimensionalityReductionsData.map((reduction, index) => ({
      dimensionalityReduction: reduction,
      publication: publicationsData[index],
      sdgPrediction: sdgPredictionsData[index]
    }));
    console.log(combinedData); // DEBUG



    // Update selected data in the stores, initially set all
    dimensionalityReductionsStore.selectedPartitionedReductions = dimensionalityReductionsStore.partitionedReductions;
    publicationsStore.selectedPartitionedPublications = publicationsStore.partitionedPublications;
    sdgPredictionsStore.selectedPartitionedSDGPredictions = sdgPredictionsStore.partitionedSDGPredictions;


    // Get the color for the selected SDG
    const selectedSDGColor = sdgsStore.getColorBySDG(sdg);


    const scatterData = {
      x: combinedData.map(d => d.dimensionalityReduction.xCoord),
      y: combinedData.map(d => d.dimensionalityReduction.yCoord),
      mode: 'markers',
      type: 'scatter',
      marker: {
        size: combinedData.map(d => (mode === 'top1' ? d.sdgPrediction.entropy * 10 : 10)),
        symbol: "hexagon2",
        color: selectedSDGColor,
        line: {
          width: 2, // Adjust outline thickness
          color: combinedData.map(d => {
            if (!d.sdgPrediction) return "black"; // Default to black if no prediction

            // Find the top 2 SDG predictions
            const sortedPredictions = Object.entries(d.sdgPrediction)
              .filter(([key]) => key.startsWith('sdg')) // Only include SDG keys
              .sort(([, valA], [, valB]) => valB - valA); // Sort in descending order

            const highestSdgId = parseInt(sortedPredictions[0][0].replace('sdg', ''), 10);
            return sdgsStore.getColorBySDG(highestSdgId); // Outline color is highest SDG prediction
          }),
        },

        opacity: 0.7
      },
      text: combinedData.map(d =>
        ` Title: ${d.publication.title} <br>
          X: ${d.dimensionalityReduction.xCoord.toFixed(2)} <br>
          Y: ${d.dimensionalityReduction.yCoord.toFixed(2)}
`),
      hoverinfo: 'text'
    };

    const layout = {
      title: `Scatter Plot for Level ${level}`,
      type: 'scattergl',
      width: width,
      height: height,
      margin: { t: 40, r: 20, b: 40, l: 40 },
      xaxis: {
        visible: false
      },
      yaxis: {
        visible: false
      },
      dragmode: 'lasso',
      showlegend: false,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot(container, [scatterData], layout);

    container.on('plotly_selected', function (eventData) {
      if (eventData && eventData.points) {
        const selectedIndices = eventData.points.map(pt => pt.pointNumber);

        // Update selected data in the stores
        const selectedSDGPredictions = selectedIndices.map(index => combinedData[index].sdgPrediction);
        const selectedPublications = selectedIndices.map(index => combinedData[index].publication);
        const selectedReductions = selectedIndices.map(index => combinedData[index].dimensionalityReduction);

        sdgPredictionsStore.selectedPartitionedSDGPredictions = selectedSDGPredictions;
        publicationsStore.selectedPartitionedPublications = selectedPublications;
        dimensionalityReductionsStore.selectedPartitionedReductions = selectedReductions;
      }
    });

    container.on('plotly_doubleclick', function () {
      Plotly.relayout(container, {
        'xaxis.range': [0, 100],
        'yaxis.range': [0, 100]
      });
    });
  });
}
