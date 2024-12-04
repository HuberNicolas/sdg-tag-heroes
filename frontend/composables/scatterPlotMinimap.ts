import * as d3 from "d3";
import * as fc from "d3fc";
import { computed, watch } from "vue";
import { usePublicationsStore } from "~/stores/publications";
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import {useSDGStore} from "~/stores/sdgs";

const hardcodedSDG = 2
const hardcodedLevel = 1

// Function to create the scatter plot and minimap
export function createScatterPlotMinimap() {

  const publicationStore = usePublicationsStore();
  const dimensionalityStore = useDimensionalityReductionsStore();
  const sdgStore = useSDGStore();


  // Use the getters directly with `computed` to make them reactive
  const publicationsForLevel = computed(() =>
    publicationStore.getPublications(hardcodedSDG, hardcodedLevel)
  );

  const reductionsForLevel = computed(() =>
    dimensionalityStore.getReductionsForLevel(hardcodedSDG, hardcodedLevel)
  );


  // Watch both `computed` properties
  watch(
    [publicationsForLevel, reductionsForLevel],
    ([newPublications, newReductions], [oldPublications, oldReductions]) => {
      if (newPublications && newReductions) {
        //console.log('Publications and reductions are loaded.');
        initScatterPlot(newPublications, newReductions);
      }
    },
    { immediate: true }
  );

function prepareData(newPublications, newReductions) {
  // "Zip" the data by matching `publication_id`
  return newReductions
    .filter(reduction => {
      // Only include reductions that have a matching publication
      const hasPublication = newPublications[reduction.publication_id];
      if (!hasPublication) {
        console.warn(
          `No publication found for reduction with publication_id: ${reduction.publication_id}`
        );
      }
      return hasPublication; // Include only if publication exists
    })
    .map(reduction => {
      const publication = newPublications[reduction.publication_id];

      return {
        reduction_id: reduction.dim_red_id, // Reduction ID
        publication_id: reduction.publication_id, // Matching Publication ID
        reduction_shorthand: reduction.reduction_shorthand, // Reduction details
        reduction_technique: reduction.reduction_technique,
        x: reduction.x_coord, // makes life easier
        y: reduction.y_coord, // makes life easier
        z_coord: reduction.z_coord,
        // Include publication details
        publication_title: publication.title,
        publication_year: publication.year,
        publication_publisher: publication.publisher,
        publication_description: publication.description,
        authors: publication.authors, // List of authors
        score: 1
      };
    });
}

function initScatterPlot(newPublications, newReductions) {
  const data = prepareData(newPublications, newReductions);
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
        .style('fill', d => d.color);

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
                      <strong>Selected Point Details:</strong><br>
                      <strong>Coordinates:</strong> (${closest.x.toFixed(2)}, ${closest.y.toFixed(2)})<br>
                      <strong>Score:</strong> ${closest.score}<br>
                      <strong>Title:</strong> ${closest.publication_title}<br>
                      <strong>Year:</strong> ${closest.publication_year}<br>
                      <strong>Publisher:</strong> ${closest.publication_publisher}<br>
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
    console.log('Visible Data Points:', brushedPoints);

    dimensionalityStore.setSelectedPoints(brushedPoints); // Update the store with selected points
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
  }

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
