import { onMounted } from 'vue';
import { createScatterPlot } from './scatterPlot';

export default function useScatterPlot() {
  onMounted(() => {
    createScatterPlot();
  });
}


