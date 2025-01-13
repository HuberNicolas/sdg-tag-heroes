<template>
  <div class="grid grid-cols-3">
    <div
      v-for="(raincloud, index) in raincloudData"
      :key="index"
      :id="`raincloud-${index}`"
      class="raincloud col-span-1"
    >
      {{ `raincloud-${index}` }}
    </div>
  </div>
</template>


<script setup lang="ts">
import * as d3 from 'd3';
import { nextTick, computed, watch } from 'vue';
import { createRaincloudPlot } from '~/composables/raincloudPlot';



const raincloudData = computed(() => {


  const generate = (count = 800) => {
    const spread = d3.randomUniform(10, 50)()
    const center = d3.randomNormal(500, spread)()
    const jitter = d3.randomUniform(10, 100)
    const direction = () => Math.random() > 0.5 ? 1 : -1
    const base = d3.randomNormal(center, spread)
    const random = () => Math.round(base() + jitter() * direction())
    const data = Array.from({length: count})
      .fill(null)
      .map(random)
      .sort(d3.ascending)
    return data
  }


  
  return ([generate(20), generate(4), generate(10)])

});

const options = {
  width: 500,
  height: 500,
};

watch(
  raincloudData,
  async (newData) => {
    console.log('Data passed to raincloud plot:', newData);

    await nextTick(); // Wait for DOM updates

    newData.forEach((data, index) => {
      const containerId = `raincloud-${index}`;
      console.log(`Rendering raincloud for container: ${containerId}`);
      createRaincloudPlot(containerId, data, options);
    });
  },
  { immediate: true }
);
</script>


<style scoped>
.raincloud {
  width: 500px;
  height: 500px;
  background-color: lightgray;
}
</style>
