import { onMounted } from 'vue';
import { createScatterPlotWebGL } from './scatterPlotWebGL';

export default function useScatterPlotWebGL() {
  onMounted(() => {
    createScatterPlotWebGL();
  });
}


