import Plotly from 'plotly.js-dist';

const sdgColors = [
  '#e5243b', '#dda63a', '#4c9f38', '#c5192d',
  '#ff3a21', '#26bde2', '#fcc30b', '#a21942',
  '#fd6925', '#dd1367', '#fd9d24', '#bf8b2e',
  '#3f7e44', '#0a97d9', '#56c02b', '#00689d',
  '#19486a'
];

export function createScatterPlot(container, width, height, mode = 'top1') {
  // Generate fake data
  const data = Array.from({ length: 1000 }, () => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    z: Math.random() * 100,
    entropy: Math.random() * 5,
    predictions: Array.from({ length: 17 }, () => Math.random())
  }));

  // Prepare plot data
  const scatterData = {
    x: data.map(d => d.x),
    y: data.map(d => d.y),
    mode: 'markers',
    type: 'scatter',
    marker: {
      size: data.map(d => (mode === 'entropy' ? d.entropy * 5 : 10)), // Adjust size for entropy mode
      color: data.map(d => {
        if (mode === 'normal') return 'steelblue';
        if (mode === 'top1') {
          const topIdx = d.predictions.indexOf(Math.max(...d.predictions));
          return sdgColors[topIdx];
        }
        return 'steelblue';
      }),
      opacity: 0.7
    },
    text: data.map(d => `X: ${d.x.toFixed(2)}<br>Y: ${d.y.toFixed(2)}`), // Tooltip content
    hoverinfo: 'text' // Show custom tooltip text
  };

  // Define layout
  const layout = {
    title: 'Scatter Plot',
    width: width,
    height: height,
    margin: { t: 40, r: 20, b: 40, l: 40 },
    "xaxis": {
      "visible": false
    },
    "yaxis": {
      "visible": false
    },
    dragmode: 'lasso', // Enable lasso selection for brushing
    showlegend: false,
    // Transparent background
    paper_bgcolor:'rgba(0,0,0,0)',
    plot_bgcolor:'rgba(0,0,0,0)'
  };

  // Render plot
  Plotly.newPlot(container, [scatterData], layout);

  // Handle brushing and zooming
  container.on('plotly_selected', function (eventData) {
    if (eventData && eventData.points) {
      const selectedPoints = eventData.points.map(pt => ({
        x: pt.x,
        y: pt.y
      }));
      console.log('Selected Points:', selectedPoints);
    }
  });

  // Double-click to reset zoom
  container.on('plotly_doubleclick', function () {
    Plotly.relayout(container, {
      'xaxis.range': [0, 100],
      'yaxis.range': [0, 100]
    });
  });
}
