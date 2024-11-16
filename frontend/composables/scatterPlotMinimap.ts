import * as d3 from 'd3';
import * as fc from 'd3fc';

// Function to create the scatter plot and minimap
export function createScatterPlotMinimap() {
  const random = d3.randomNormal(0, 0.2);
  const sqrt3 = Math.sqrt(3);
  const points0 = d3.range(30).map(() => [random() + sqrt3, random() + 1, 0]);
  const points1 = d3.range(30).map(() => [random() - sqrt3, random() + 1, 1]);
  const points2 = d3.range(30).map(() => [random(), random() - 1, 2]);
  const data = d3.merge([points0, points1, points2]).map(d => ({
    ...d,
    score: Math.floor(Math.random() * 100)
  }));

  // Create a quadtree for efficient point lookup
  const quadtree = d3.quadtree()
    .x(d => d[0])
    .y(d => d[1])
    .addAll(data);

  const yExtent = fc
    .extentLinear()
    .accessors([d => d[1]])
    .pad([0.1, 0.1]);

  const xExtent = fc
    .extentLinear()
    .accessors([d => d[0]])
    .pad([0.1, 0.1]);

  const x = d3.scaleLinear().domain(xExtent(data));
  const y = d3.scaleLinear().domain(yExtent(data));
  const color = d3.scaleOrdinal(d3.schemeCategory10);

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

  // Update pointSeries to handle mouse events for showing tooltip
  const pointSeries = fc
    .seriesSvgPoint()
    .crossValue(d => d[0])
    .mainValue(d => d[1])
    .size(15)
    .decorate(selection => {
      selection.enter()
        .style('fill', d => color(d[2]));

      // Add mouse event listeners to the entire plot area
      d3.select('#scatter-plot')
        .on('mousemove', function (event) {
          const [mouseX, mouseY] = d3.pointer(event);

          // Invert the mouse position to get data coordinates
          const xValue = x.invert(mouseX);
          const yValue = y.invert(mouseY);

          // Find the closest point using the quadtree
          const closest = quadtree.find(xValue, yValue);

          if (closest) {
            tooltip
              .style('opacity', 1)
              .html(`Score: ${closest.score}`)
              .style('left', `${event.pageX + 10}px`)
              .style('top', `${event.pageY + 10}px`);
          } else {
            tooltip.style('opacity', 0);
          }
        })
        .on('mouseout', () => {
          tooltip.style('opacity', 0);
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
        updateMinimap(null, null); // Clear the minimap selection
        render();
      }
    } else {
      x.domain(e.xDomain);
      y.domain(e.yDomain);
      updateMinimap(e.xDomain, e.yDomain);
      render();
    }
    // Log only the data points that are visible in the current x and y domain
    const visibleData = data.filter(d =>
      x.domain()[0] <= d[0] && d[0] <= x.domain()[1] &&
      y.domain()[0] <= d[1] && d[1] <= y.domain()[1]
    );
    console.log('Visible Data Points:', visibleData);
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
      .transition()
      .call(scatterPlot);
  }

  // Create the minimap
  const minimapX = d3.scaleLinear().domain(xExtent(data)).range([0, 100]);
  const minimapY = d3.scaleLinear().domain(yExtent(data)).range([100, 0]);

  const minimapPointSeries = fc
    .seriesSvgPoint()
    .crossValue(d => d[0])
    .mainValue(d => d[1])
    .size(5)
    .decorate(selection => {
      selection.enter()
        .style('fill', d => color(d[2]));
    });

  const minimap = fc.chartCartesian(minimapX, minimapY).svgPlotArea(minimapPointSeries);

  function renderMinimap() {
    d3.select('#scatter-plot-minimap')
      .datum(data)
      .call(minimap);

    // Add a blue rectangle for the brush extent
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
      .attr('fill', 'blue')
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
