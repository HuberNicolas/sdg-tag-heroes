import { onMounted } from 'vue';
import { createScatterPlotMinimap } from './scatterPlotMinimap';

export default function useScatterPlotMinimap() {
  onMounted(() => {
    createScatterPlotMinimap();
  });
}


