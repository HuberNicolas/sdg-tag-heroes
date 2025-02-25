import Plotly from 'plotly.js-dist';
import { watch } from 'vue';
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useCollectionsStore } from "~/stores/collections";
import { useGameStore } from "~/stores/game";
import { useSDGsStore } from "~/stores/sdgs";

export function createScatterPlot(container, width, height, mode = 'top1') {
  const dimensionalityReductionsStore = useDimensionalityReductionsStore();
  const publicationsStore = usePublicationsStore();
  const sdgPredictionsStore = useSDGPredictionsStore();
  const labelDecisionsStore = useLabelDecisionsStore();
  const gameStore = useGameStore();
  const sdgsStore = useSDGsStore();
  const collectionsStore = useCollectionsStore();

  const level = gameStore.getLevel;
  const sdg = gameStore.getSDG;
  let scatterPlotInstance = null; // Store Plotly instance
  let selectedPoint = null; // Store clicked point coordinates
  let highlightMarker = null;
  let hoverHighlightMarker = null
  let userMarker = null;
  let scatterData = null;

  // Fetch partitioned data from all stores
  const fetchData = async () => {
    const reductionShorthand = 'UMAP-15-0.0-2';

    await Promise.all([
      dimensionalityReductionsStore.fetchDimensionalityReductionsBySDGAndLevel(sdg, reductionShorthand, level),
      publicationsStore.fetchPublicationsForDimensionalityReductions(sdg, reductionShorthand, level),
      sdgPredictionsStore.fetchSDGPredictionsByLevel(sdg, reductionShorthand, level),
      sdgsStore.fetchSDGs(),
      collectionsStore.fetchCollections(),
      labelDecisionsStore.fetchSDGLabelDecisionsForReduction(sdg, reductionShorthand, level),
    ]);
  };

  fetchData().then(() => {
    const dimensionalityReductionsData = dimensionalityReductionsStore.sdgLevelReductions;
    const publicationsData = publicationsStore.sdgLevelPublications;
    const sdgPredictionsData = sdgPredictionsStore.sdgLevelSDGPredictions;

    // Get selected collections
    const selectedCollectionIds = new Set(collectionsStore.selectedCollections.map(c => c.collectionId));

    // Calculate publication count per collection
    const collectionPublicationCounts = {};
    publicationsData.forEach((pub) => {
      if (pub.collectionId) {
        if (!collectionPublicationCounts[pub.collectionId]) {
          collectionPublicationCounts[pub.collectionId] = 0;
        }
        collectionPublicationCounts[pub.collectionId]++;
      }
    });

    // Update the store with new collection publication counts
    collectionsStore.collectionsCount = collectionPublicationCounts;


    console.log(publicationsData);
    console.log(selectedCollectionIds);
    // Filter publications
    const filteredPublicationsData = publicationsData.filter(publication =>
      publication.collectionId && selectedCollectionIds.has(publication.collectionId)
    );

    console.log(publicationsData)
    let combinedData = dimensionalityReductionsData.map((reduction, index) => ({
      dimensionalityReduction: reduction,
      publication: filteredPublicationsData[index],
      sdgPrediction: sdgPredictionsData[index],
    }));

    console.log(combinedData);

    // Get the color for the selected SDG
    const selectedSDGColor = sdgsStore.getColorBySDG(sdg);

    // Scatter plot data
    scatterData = {
      x: combinedData.map(d => d.dimensionalityReduction.xCoord),
      y: combinedData.map(d => d.dimensionalityReduction.yCoord),
      mode: 'markers',
      type: 'scatter',
      marker: {
        size: combinedData.map(d => (mode === 'top1' ? d.sdgPrediction.entropy * 10 : 10)),
        symbol: "hexagon2",
        color: selectedSDGColor,
        line: {
          width: 5, // Adjust outline thickness
          color: combinedData.map(d => {
            if (!d.sdgPrediction) return "black";

            // Find the highest SDG prediction
            const sortedPredictions = Object.entries(d.sdgPrediction)
              .filter(([key]) => key.startsWith('sdg'))
              .sort(([, valA], [, valB]) => valB - valA);

            const highestSdgId = parseInt(sortedPredictions[0][0].replace('sdg', ''), 10);
            return sdgsStore.getColorBySDG(highestSdgId);
          }),
        },
        opacity: 0.7,
      },
      text: combinedData.map(d =>
        ` Title: ${d.publication.title} <br>
          X: ${d.dimensionalityReduction.xCoord.toFixed(2)} <br>
          Y: ${d.dimensionalityReduction.yCoord.toFixed(2)}`
      ),
      hoverinfo: 'text',
    };

    // Initial user marker
    //userMarker = createUserMarker();

    const layout = {
      title: ``, //`Scatter Plot for Level ${level}`,
      type: 'scattergl',
      width: width,
      height: height,
      margin: { t: 5, r: 5, b: 70, l: 5 },
      xaxis: { visible: false },
      yaxis: { visible: false },
      dragmode: 'lasso',
      showlegend: false,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
    };

    // Render the plot
    scatterPlotInstance = Plotly.newPlot(container, userMarker ? [scatterData, userMarker] : [scatterData], layout);


    // Watch for changes in selected collections and update the plot
    watch(
      () => collectionsStore.selectedCollections,
      () => {
        console.log("Selected collections updated! Redrawing scatter plot...");
        updateScatterPlot();
      },
      { deep: true }
    );


    // Listen for user coordinate updates
    watch(
      () => gameStore.getUserCoordinates,
      () => {
        updateUserMarker();
      },
      { deep: true }
    );

    // user clicked Scenario button
    watch(
      [
        () => dimensionalityReductionsStore.scenarioTypeReductions,
        () => publicationsStore.scenarioTypePublications,
        () => sdgPredictionsStore.scenarioTypeSDGPredictions,
      ],
      () => {
        console.log("Scenario data updated! Updating scatter plot...");
        updateScatterPlot();
      },
      { deep: true }
    );

    watch(
      () => publicationsStore.hoveredPublication,
      (newHoveredPublication) => {
        if (newHoveredPublication) {
          // Find the corresponding point in the combinedData
          const hoveredPoint = combinedData.find(
            (d) => d.publication.publicationId === newHoveredPublication.publicationId
          );

          if (hoveredPoint) {
            // Update the highlighted point in the scatter plot
            updateHighlightedPointFromHover({
              x: hoveredPoint.dimensionalityReduction.xCoord,
              y: hoveredPoint.dimensionalityReduction.yCoord,
            });
          }
        } else {
          // If no publication is hovered, remove the highlight
          removeHoverHighlightMarker();
        }
      },
      { deep: true }
    );


    // Selection events
    container.on('plotly_selected', function (eventData) {
      if (eventData && eventData.points) {
        // Filter out any points that are user markers (star symbol)
        const selectedIndices = eventData.points
          .filter(pt => pt.data.text[0] !== '📍') // Exclude user markers with '📍'
          .map(pt => pt.pointNumber); // Map to indices of valid points

        const selectedSDGPredictions = selectedIndices.map(index => combinedData[index].sdgPrediction);
        const selectedPublications = selectedIndices.map(index => combinedData[index].publication);
        const selectedReductions = selectedIndices.map(index => combinedData[index].dimensionalityReduction);

        sdgPredictionsStore.selectedPartitionedSDGPredictions = selectedSDGPredictions;
        publicationsStore.selectedPartitionedPublications = selectedPublications;
        dimensionalityReductionsStore.selectedPartitionedReductions = selectedReductions;
      }
    });

    container.on('plotly_doubleclick', function () {
      Plotly.relayout(container, { 'xaxis.range': [0, 100], 'yaxis.range': [0, 100] });
    });

    container.on('plotly_click', function (eventData) {
      if (eventData && eventData.points.length > 0) {
        const clickedPoint = eventData.points[0];
        const clickedIndex = clickedPoint.pointNumber;

        // Ensure the clicked marker is NOT the user marker
        if (clickedPoint.data.text === "📍") return;

        // Get the selected publication
        const selectedPublication = combinedData[clickedIndex]?.publication;
        if (selectedPublication) {
          publicationsStore.setSelectedPublication(selectedPublication);
          publicationsStore.selectedPartitionedPublications([selectedPublication]);
          console.log("Selected Publication:", selectedPublication);

          // Store the clicked point's coordinates
          selectedPoint = {
            x: clickedPoint.x,
            y: clickedPoint.y
          };

          updateHighlightedPoint();
        }
      }
    });

    container.on('plotly_hover', function (eventData) {
      if (eventData && eventData.points.length > 0) {
        const hoveredIndex = eventData.points[0].pointNumber;
        const hoveredPub = combinedData[hoveredIndex]?.publication;
        if (hoveredPub) {
          publicationsStore.setHoveredPublication(hoveredPub);
        }
      }
    });

    container.on('plotly_unhover', function () {
      publicationsStore.setHoveredPublication(null);
    });


    // Function to create user marker
    function createUserMarker() {
      const userCoordinates = gameStore.getUserCoordinates;
      if (!userCoordinates) return null;

      return {
        mode: 'text',
        x: [userCoordinates.x_coord],
        y: [userCoordinates.y_coord],
        text: ['📍'],
        type: 'scatter',
        textfont: {
          size: 25,
          color: 'black'
        }
      };
    }

    function updateHighlightedPoint() {
      if (!selectedPoint) return;

      highlightMarker = {
        x: [selectedPoint.x],
        y: [selectedPoint.y],
        mode: "markers",
        type: "scatter",
        marker: {
          size: 50, // Slightly larger to create a circle effect
          symbol: "circle",
          color: "rgba(0, 0, 0, 0.1)", // Transparent black
          line: {
            width: 3,
            color: "black",
          },
          opacity: 1.0,
        },
        text: [`Selected Point`],
        hoverinfo: "text",
      };

      Plotly.react(container, [scatterData, highlightMarker, userMarker].filter(Boolean), layout);
    }
    function updateScatterPlot() {
      const dimensionalityReductionsData = dimensionalityReductionsStore.sdgLevelReductions;
      const publicationsData = publicationsStore.sdgLevelPublications;
      const sdgPredictionsData = sdgPredictionsStore.sdgLevelSDGPredictions;

      // Scenario Data
      const scenarioReductionsData = dimensionalityReductionsStore.scenarioTypeReductions;
      const scenarioPublicationsData = publicationsStore.scenarioTypePublications;
      const scenarioPredictionsData = sdgPredictionsStore.scenarioTypeSDGPredictions;

      // Get selected collections
      const selectedCollectionIds = new Set(collectionsStore.selectedCollections.map(c => c.collectionId));


      // Identify collections used in scenario publications but not yet selected
      const missingCollections = scenarioPublicationsData
        .filter(pub => pub.collectionId && !selectedCollectionIds.has(pub.collectionId)) // Find missing ones
        .map(pub => pub.collectionId);

      if (missingCollections.length > 0) {
        console.log("Adding missing scenario collections:", missingCollections);

        // Update store to include missing collections
        collectionsStore.setSelectedCollections([...collectionsStore.selectedCollections, ...missingCollections]);
      }

      // Update selected collection IDs after adding missing ones
      const updatedCollectionIds = new Set(collectionsStore.selectedCollections.map(c => c.collectionId));

      // Recalculate publication counts for the updated collection list
      const updatedCollectionPublicationCounts = {};
      publicationsData.forEach((pub) => {
        if (pub.collectionId && updatedCollectionIds.has(pub.collectionId)) {
          if (!updatedCollectionPublicationCounts[pub.collectionId]) {
            updatedCollectionPublicationCounts[pub.collectionId] = 0;
          }
          updatedCollectionPublicationCounts[pub.collectionId]++;
        }
      });

      // Update the store with recalculated collection publication counts
      collectionsStore.collectionsCount = updatedCollectionPublicationCounts;

      // Filter publications
      const filteredPublicationsData = publicationsData.filter(publication =>
        publication.collectionId && updatedCollectionIds.has(publication.collectionId)
      );
      console.log(filteredPublicationsData);


      // Merge data while tagging scenario points
      combinedData = [
        ...dimensionalityReductionsData
          .map((reduction) => {
            const publication = filteredPublicationsData.find(pub => pub.publicationId === reduction.publicationId);
            const sdgPrediction = sdgPredictionsData.find(pred => pred.publicationId === reduction.publicationId);
            return publication && sdgPrediction
              ? { dimensionalityReduction: reduction, publication, sdgPrediction, isScenario: false }
              : null;
          })
          .filter(Boolean), // Remove null values

        ...scenarioReductionsData
          .map((reduction, index) => {
            const publication = scenarioPublicationsData[index];
            const sdgPrediction = scenarioPredictionsData[index];
            return publication && sdgPrediction
              ? { dimensionalityReduction: reduction, publication, sdgPrediction, isScenario: true }
              : null;
          })
          .filter(Boolean), // Remove null values
      ];


      console.log(combinedData)

      // Check for missing or undefined properties
      combinedData.forEach((d, i) => {
        if (!d.publication || !d.publication.title) {
          console.warn(`Missing publication data at index ${i}`);
        }
        if (!d.sdgPrediction) {
          console.warn(`Missing SDG prediction at index ${i}`);
        }
      });

      // Define scatter data
      scatterData = {
        x: combinedData.map(d => d.dimensionalityReduction.xCoord),
        y: combinedData.map(d => d.dimensionalityReduction.yCoord),
        mode: "markers",
        type: "scatter",
        marker: {
          size: combinedData.map(d => (mode === "top1" ? d.sdgPrediction?.entropy * 10 : 10)),
          symbol: combinedData.map(d => (d.isScenario ? "diamond" : "hexagon2")), // Different glyph for scenarios
          color: combinedData.map(d => (d.isScenario ? selectedSDGColor : selectedSDGColor)), // Keep original color but differentiate scenarios
          line: {
            width: combinedData.map(d => (d.isScenario ? 3 : 5)), // Slightly thinner outline for scenario pubs
            color: combinedData.map(d => {
              if (!d.sdgPrediction) return "black";

              // Determine highest SDG prediction
              const sortedPredictions = Object.entries(d.sdgPrediction)
                .filter(([key]) => key.startsWith("sdg"))
                .sort(([, valA], [, valB]) => valB - valA);

              const highestSdgId = parseInt(sortedPredictions[0][0].replace("sdg", ""), 10);
              return sdgsStore.getColorBySDG(highestSdgId);
            }),
          },
          opacity: 0.7,
        },
        text: combinedData.map(d =>
          `${d.publication.title} <br> X: ${d.dimensionalityReduction.xCoord.toFixed(2)} <br> Y: ${d.dimensionalityReduction.yCoord.toFixed(2)}`
        ),
        hoverinfo: "text",
      };

      // Update the plot with both default and scenario points
      Plotly.react(container, [scatterData, hoverHighlightMarker, userMarker].filter(Boolean), layout);
    }

    function updateHighlightedPointFromHover(coordinates) {
      // Create a highlight marker for hover (you can style it differently from the selected marker)
      hoverHighlightMarker = {
        x: [coordinates.x],
        y: [coordinates.y],
        mode: "markers",
        type: "scatter",
        marker: {
          size: 40,
          symbol: "circle",
          color: "rgba(0, 0, 0, 0.1)", // semi-transparent overlay
          line: {
            width: 4,
            color: "black" // selectedSDGColor,
          },
        },
      };

      // Re-render the plot with the hover marker included.
      // Make sure to merge it with your existing data (e.g., scatterData and any other markers)
      Plotly.react(container, [scatterData, hoverHighlightMarker, userMarker].filter(Boolean), layout);
    }

    function removeHoverHighlightMarker() {
      // Remove the hover highlight by re-rendering without the marker.
      Plotly.react(container, [scatterData, userMarker].filter(Boolean), layout);
    }


    // Function to update user marker dynamically
    function updateUserMarker() {
      userMarker = createUserMarker();
      if (!userMarker) return;

      Plotly.react(container, [scatterData, hoverHighlightMarker, userMarker].filter(Boolean), layout);
    }
  });
}
