import * as d3 from "d3";
import * as fc from "d3fc";
import { computed, watch } from "vue";
import { useRouter } from 'vue-router';
import { usePublicationsStore } from "~/stores/publications";
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import {useSDGStore} from "~/stores/sdgs";


// Function to create the scatter plot and minimap
export function createScatterPlotMinimap() {

  const publicationStore = usePublicationsStore();
  const dimensionalityStore = useDimensionalityReductionsStore();
  const sdgStore = useSDGStore();
  const predictionsStore = usePredictionsStore();
  const router = useRouter();

  const selectedSDG = sdgStore.getSelectedGoal;
  const currentLevel = dimensionalityStore.getCurrentLevel;

  // Use the getters directly with `computed` to make them reactive
  const publicationsForLevel = computed(() =>
    publicationStore.getPublications(selectedSDG, currentLevel)
  );

  const reductionsForLevel = computed(() =>
    dimensionalityStore.getReductionsForLevel(selectedSDG, currentLevel)
  );

  const predictionsForLevel = computed(() =>
    predictionsStore.getPredictionsForLevel(selectedSDG, currentLevel)
  )


  // Watch both `computed` properties
  watch(
    [publicationsForLevel, reductionsForLevel, predictionsForLevel],
    ([newPublications, newReductions, newPredictions], [oldPublications, oldReductions, oldPredictions]) => {
      if (newPublications && newReductions && newPredictions) {
        //console.log('Publications and reductions are loaded.');
        initScatterPlot(newPublications, newReductions, newPredictions);
      }
    },
    { immediate: true }
  );

  // Watch for userCoordinates updates
  watch(
    () => dimensionalityStore.userCoordinates,
    (newUserCoordinates) => {
      if (newUserCoordinates) {
        console.log("User coordinates loaded:", newUserCoordinates);

        // Re-initialize the scatter plot with updated user coordinates
        initScatterPlot(
          publicationsForLevel.value,
          reductionsForLevel.value,
          predictionsForLevel.value
        );
      }
    },
    { immediate: true }
  );

  function prepareData(newPublications, newReductions, newPredictions) {
    const predictionArray = Array.isArray(newPredictions)
      ? newPredictions
      : Object.values(newPredictions);

    // "Zip" the data by matching `publication_id`
    const data = newReductions
      .filter(reduction => {
        const hasPublication = newPublications[reduction.publication_id];
        return hasPublication; // Include only if publication exists
      })
      .map(reduction => {
        const publication = newPublications[reduction.publication_id];
        const prediction = predictionArray.find(
          p => p.publication_id === reduction.publication_id
        );

        const score = prediction ? prediction[`sdg${selectedSDG}`] || 1 : 1;

        return {
          reduction_id: reduction.dim_red_id,
          publication_id: reduction.publication_id,
          reduction_shorthand: reduction.reduction_shorthand,
          reduction_technique: reduction.reduction_technique,
          x: reduction.x_coord,
          y: reduction.y_coord,
          z_coord: reduction.z_coord,
          publication_title: publication.title,
          publication_year: publication.year,
          publication_publisher: publication.publisher,
          publication_description: publication.description,
          authors: publication.authors,
          score: score,
          color: sdgStore.getSelectedGoalColor(selectedSDG),
        };
      });

    // Append the user coordinates as an additional point
    if (dimensionalityStore.userCoordinates) {
      console.log("has User coordinates")
      const userPoint = {
        reduction_id: null,
        publication_id: null, // No publication associated
        reduction_shorthand: "User",
        reduction_technique: "Manual",
        x: dimensionalityStore.userCoordinates.x,
        y: dimensionalityStore.userCoordinates.y,
        z_coord: dimensionalityStore.userCoordinates.z,
        publication_title: "User Point",
        publication_year: "",
        publication_publisher: "",
        publication_description: "",
        authors: [],
        score: 1, // Default score
        color: "black", // Use a distinctive color for the user point
      };

      data.push(userPoint);
    }

    return data;
  }


function initScatterPlot(newPublications, newReductions, newPredictions) {
  const data = prepareData(newPublications, newReductions, newPredictions);
  // Create a quadtree for efficient point lookup
  const quadtree = d3.quadtree()
    .x(d => d.x)
    .y(d => d.y)
    .addAll(data);

  const yExtent = fc
    .extentLinear()
    .accessors([d => d.y])
    .pad([0.1, 0.1]);

  const xExtent = fc
    .extentLinear()
    .accessors([d => d.x])
    .pad([0.1, 0.1]);

  const x = d3.scaleLinear().domain(xExtent(data));
  const y = d3.scaleLinear().domain(yExtent(data));

  // Create a tooltip div and append it to the body
  const tooltip = d3.select('body')
    .append('div')
    .attr('class', 'tooltip')
    .style('position', 'absolute')
    .style('background-color', 'white')
    .style('border', '1px solid #ddd')
    .style('padding', '5px')
    .style('border-radius', '4px')
    .style('pointer-events', 'none')
    .style('opacity', 0);

  function distance(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
  }

  const detectionBorder = 25;

  // Add click event to the main container to simulate click on points
  d3.select('#scatter-plot')
    .on('click', function (event) {
      const [mouseX, mouseY] = d3.pointer(event, this);

      // Convert the mouse position to data coordinates
      const xValue = x.invert(mouseX);
      const yValue = y.invert(mouseY);

      // Use the quadtree to find the closest point to the mouse click
      const closest = quadtree.find(xValue, yValue);

      if (closest) {
        // Convert the closest data point to screen coordinates
        const pointX = x(closest.x);
        const pointY = y(closest.y);

        // Calculate the distance in pixels between the mouse click and the closest point
        const distanceToPointPixels = distance(mouseX, mouseY, pointX, pointY);

        // Check if the distance is within the detection border
        if (distanceToPointPixels <= detectionBorder) {
          // Trigger the click event for the closest point
          // console.log('Point clicked:', closest);
        }
      }
    });



  // Update pointSeries to handle mouse events for showing tooltip
  const pointSeries = fc
    .seriesSvgPoint()
    .crossValue(d => d.x)
    .mainValue(d => d.y)
    .size(15)
    .decorate(selection => {
      selection.enter()
        .style('fill', d => d.color)
        .style('stroke', d => (d.reduction_shorthand === "User" ? "black" : null))
        .style('stroke-width', d => (d.reduction_shorthand === "User" ? 10 : 0));

      // Add mouse event listeners to the entire plot area
      d3.select('#scatter-plot')
        .on('mousemove', function (event) {
          const [mouseX, mouseY] = d3.pointer(event);

          // Invert the mouse position to get data coordinates
          const xValue = x.invert(mouseX);
          const yValue = y.invert(mouseY);

          // Find the closest point using the quadtree
          const closest = quadtree.find(xValue, yValue);

          // Convert the closest data point to screen coordinates for distance calculation
          const pointX = x(closest.x);
          const pointY = y(closest.y);

          //const distanceToPoint = distance(xValue, yValue, closest[0], closest[1]);
          const distanceToPointPixels = distance(mouseX, mouseY, pointX, pointY);

          //console.table([[mouseX, mouseY], [xValue, yValue], [closest[0], closest[1]], [pointX, pointY], ])
          //console.log(distanceToPoint, distanceToPointPixels);

          if (closest) {
            if (distanceToPointPixels <= detectionBorder) {
              // Get the scatter plot element's position relative to the page
              const scatterPlotElement = d3.select('#scatter-plot').node();
              const scatterPlotRect = scatterPlotElement.getBoundingClientRect();

              tooltip
                .style('opacity', 1)
                .html(`Score: ${closest.score}`)
                .style('left', `${scatterPlotRect.left + pointX}px`)
                .style('top', `${scatterPlotRect.top + pointY}px`);

              // Update the coordinates, score, and other details in the bottom control div
              d3.select('#scatter-plot-selected-point')
                .html(`
                      <strong>Publication Details:</strong><br>
                      <strong>Title:</strong> ${closest.publication_title}<br>
                      <strong>Coordinates:</strong> (${closest.x.toFixed(2)}, ${closest.y.toFixed(2)})<br>
                      <strong>Prediction Score:</strong> ${closest.score}<br>
                      <strong>Year:</strong> ${closest.publication_year}<br>
                    `);
            }

            else {
              tooltip.style('opacity', 0);
              d3.select('#scatter-plot-selected-point').html('');
            }
          } else {
            tooltip.style('opacity', 0);
            d3.select('#scatter-plot-selected-point').html('');
          }
        })
        .on('mouseout', () => {
          tooltip.style('opacity', 0);
          d3.select('#scatter-plot-selected-point').html('');
        })
        .on('click', function (event) {
          const [mouseX, mouseY] = d3.pointer(event);

          // Invert the mouse position to get data coordinates
          const xValue = x.invert(mouseX);
          const yValue = y.invert(mouseY);

          // Find the closest point using the quadtree
          const closest = quadtree.find(xValue, yValue);

          if (closest) {
            // Perform an action on click, e.g., log details or highlight the point
            console.log('Point clicked:', closest);
            tooltip.style('opacity', 0);
            d3.select('#scatter-plot-selected-point').html('');
            router.push({ name: 'labeling-id', params: { id: closest.publication_id } });
          }
        });
    });

  let idleTimeout;
  const idleDelay = 350;

  const brush = fc.brush().on('end', e => {
    if (!e.selection) {
      if (!idleTimeout) {
        idleTimeout = setTimeout(() => (idleTimeout = null), idleDelay);
      } else {
        x.domain(xExtent(data));
        y.domain(yExtent(data));
        dimensionalityStore.clearSelectedPoints(); // Clear selection in the store
        dimensionalityStore.clearSelectedSummary();
        updateMinimap(null, null); // Clear the minimap selection
        render();
      }
    } else {
      x.domain(e.xDomain);
      y.domain(e.yDomain);
      updateMinimap(e.xDomain, e.yDomain);
      render();
    }
    // Filter data points within the brush extent
    const brushedPoints = data.filter(d =>
      x.domain()[0] <= d.x && d.x <= x.domain()[1] &&
      y.domain()[0] <= d.y && d.y <= y.domain()[1]
    );

    d3.select('#scatter-plot-visible-points')
      .html(`Number of Points: ${brushedPoints.length}`);
    //console.log('Visible Data Points:', brushedPoints);

    dimensionalityStore.setSelectedPoints(brushedPoints); // Update the store with selected points

    // Trigger summary computation
    dimensionalityStore.clearSelectedSummary();
    dimensionalityStore.computeSummaryForSelectedPoints();
  });

  const multi = fc
    .seriesSvgMulti()
    .series([pointSeries, brush])
    .mapping((data, index, series) => {
      switch (series[index]) {
        case pointSeries:
          return data;
        case brush:
          return null;
      }
    });

  const scatterPlot = fc.chartCartesian(x, y).svgPlotArea(multi);

  function render() {
    d3.select('#scatter-plot')
      .datum(data)
      //.transition() // could not fix error here :/
      .call(scatterPlot);

    // Add X-Axis Label
    d3.select('#scatter-plot svg')
      .append("text")
      .attr("class", "x-axis-label")
      .attr("text-anchor", "middle")
      .attr("x", "50%")
      .attr("y", "95%")
      .style("font-size", "14px")
      .text("Similarity Dimension 1");

    // Add Y-Axis Label
    d3.select('#scatter-plot svg')
      .append("text")
      .attr("class", "y-axis-label")
      .attr("text-anchor", "middle")
      .attr("transform", "rotate(-90)")
      .attr("x", -200) // Adjust position based on your chart
      .attr("y", 20)
      .style("font-size", "14px")
      .text("Similarity Dimension 2");

    // Add Chart Title
    d3.select('#scatter-plot svg')
      .append("text")
      .attr("class", "chart-title")
      .attr("text-anchor", "middle")
      .attr("x", "50%")
      .attr("y", "5%")
      .style("font-size", "18px")
      .style("font-weight", "bold")
      .text("Publication Abstracts: A Similarity Map");
  }




  // Add a keyboard event listener to reset zoom when 'r' is pressed
  d3.select('body').on('keydown', function (event) {
    if (event.key === 'r' || event.key === 'R') {
      // Reset x and y domains to their original extents
      x.domain(xExtent(data));
      y.domain(yExtent(data));

      // Clear any selection in the minimap
      updateMinimap(null, null);

      // Re-render the scatter plot and minimap
      render();
      renderMinimap();

      // Clear selected points and summaries from the store
      dimensionalityStore.clearSelectedPoints();
      dimensionalityStore.clearSelectedSummary();

      // Update UI to show the total number of points
      d3.select('#scatter-plot-visible-points').html(`Number of Points: ${data.length}`);

      console.log('Zoom reset to default view!');
    }
  });


  // Create the minimap
  const minimapX = d3.scaleLinear().domain(xExtent(data)).range([0, 100]);
  const minimapY = d3.scaleLinear().domain(yExtent(data)).range([100, 0]);

  const minimapPointSeries = fc
    .seriesSvgPoint()
    .crossValue(d => d.x)
    .mainValue(d => d.y)
    .size(5)
    .decorate(selection => {
      selection.enter()
        .style('fill', d => d.color);
    });

  const minimap = fc.chartCartesian(minimapX, minimapY).svgPlotArea(minimapPointSeries);

  function renderMinimap() {
    d3.select('#scatter-plot-minimap')
      .datum(data)
      .call(minimap);

    // Add X-Axis Label
    d3.select('#scatter-plot-minimap svg')
      .append("text")
      .attr("class", "x-axis-label")
      .attr("text-anchor", "middle")
      .attr("x", "50%")
      .attr("y", "95%")
      .style("font-size", "7px")
      .text("Similarity Dimension 1");

    // Add Y-Axis Label
    d3.select('#scatter-plot-minimap svg')
      .append("text")
      .attr("class", "y-axis-label")
      .attr("text-anchor", "middle")
      .attr("transform", "rotate(-90)")
      .attr("x", -60) // Adjust position based on your chart
      .attr("y", 10)
      .style("font-size", "7px")
      .text("Similarity Dimension 2");

    // Add Chart Title
    d3.select('#scatter-plot-minimap svg')
      .append("text")
      .attr("class", "chart-title")
      .attr("text-anchor", "middle")
      .attr("x", "50%")
      .attr("y", "5%")
      .style("font-size", "10px")
      .style("font-weight", "bold")
      .text("Minimap");


  // Add a rectangle for the brush extent
    const svg = d3.select('#scatter-plot-minimap').select('svg');

    // Ensure that the rectangle is drawn within the SVG
    const rect = svg.selectAll('rect.brush-rect').data([0]);

    rect.enter()
      .append('rect')
      .attr('class', 'brush-rect')
      .merge(rect)
      .attr('x', minimapX(x.domain()[0]))
      .attr('y', minimapY(y.domain()[1]))
      .attr('width', minimapX(x.domain()[1]) - minimapX(x.domain()[0]))
      .attr('height', minimapY(y.domain()[0]) - minimapY(y.domain()[1]))
      .attr('fill', 'black')
      .attr('opacity', 0.3);
  }

  function updateMinimap(xDomain, yDomain) {
    const rect = d3.select('#scatter-plot-minimap').select('rect.brush-rect');

    if (!xDomain || !yDomain) {
      // Clear the selection rectangle
      rect.attr('width', 0).attr('height', 0);
    } else {
      // Update the selection rectangle
      rect.attr('x', minimapX(xDomain[0]))
        .attr('y', minimapY(yDomain[1]))
        .attr('width', minimapX(xDomain[1]) - minimapX(xDomain[0]))
        .attr('height', minimapY(yDomain[0]) - minimapY(yDomain[1]));
    }
  }

  render();
  renderMinimap();
}

}
