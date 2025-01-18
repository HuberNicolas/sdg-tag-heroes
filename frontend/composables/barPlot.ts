import Plotly from 'plotly.js-dist';
import { sdgColors } from "~/constants/sdgs";


export function createBarPlot(
  container: HTMLElement,
  width: number,
  height: number,
  data: { x: string[]; y: number[] }[],
) {
  const traces = data.map((dataset, index) => ({
    x: dataset.x,
    y: dataset.y,
    name: `SDG Predictions`,
    type: 'bar',
    marker: {
      color: sdgColors.slice(0, dataset.x.length), // Apply SDG colors to bars
    },
  }));

  const layout = {
    title: 'Bar Plot',
    barmode: 'group',
    width: width,
    height: height,
    margin: { t: 40, r: 20, b: 40, l: 40 },
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

  Plotly.newPlot(container, traces, layout);
}
