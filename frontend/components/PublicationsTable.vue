<template>
  <table class="w-full border-collapse">
    <thead>
    <tr class="bg-gray-100">
      <th class="border border-gray-300 p-2">Title</th>
      <th class="border border-gray-300 p-2">Glyph</th>
      <th class="border border-gray-300 p-2">XP</th>
      <th class="border border-gray-300 p-2">Coins</th>
      <th class="border border-gray-300 p-2">Top SDG</th>
      <th class="border border-gray-300 p-2">Year</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="(item, index) in tableData" :key="index" class="hover:bg-gray-50">
      <td class="border border-gray-300 p-2">{{ item.title }}</td>
      <td class="border border-gray-300 p-2 flex items-center justify-center">
        <HexGlyph :values="item.values" :height="100" :width="80" />
      </td>
      <td class="border border-gray-300 p-2">{{ item.xp }}</td>
      <td class="border border-gray-300 p-2">{{ item.coins }}</td>
      <td class="border border-gray-300 p-2">{{ item.topSdg }}</td>
      <td class="border border-gray-300 p-2">{{ item.year }}</td>
    </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { usePublicationsStore } from '~/stores/publications';
import { useSDGPredictionsStore } from '~/stores/sdgPredictions';
import HexGlyph from '@/components/PredictionGlyph.vue';

const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();

// Map selected publications and predictions to table data
const tableData = computed(() => {
  return publicationsStore.selectedPartitionedPublications.map((pub, index) => {
    const prediction = sdgPredictionsStore.selectedPartitionedSDGPredictions[index];

    // Extract SDG values from the prediction
    const values = [
      prediction.sdg1,
      prediction.sdg2,
      prediction.sdg3,
      prediction.sdg4,
      prediction.sdg5,
      prediction.sdg6,
      prediction.sdg7,
      prediction.sdg8,
      prediction.sdg9,
      prediction.sdg10,
      prediction.sdg11,
      prediction.sdg12,
      prediction.sdg13,
      prediction.sdg14,
      prediction.sdg15,
      prediction.sdg16,
      prediction.sdg17,
    ];

    // Find the top SDG by only considering sdg1 to sdg17
    const sdgKeys = Array.from({ length: 17 }, (_, i) => `sdg${i + 1}`);
    const topSdgKey = sdgKeys.reduce((a, b) =>
      prediction[a] > prediction[b] ? a : b
    );
    const topSdg = `SDG ${topSdgKey.replace('sdg', '')}`;


    // Dummy data for XP and coins
    const xp = Math.floor(Math.random() * 100); // Random XP between 0 and 100
    const coins = Math.floor(Math.random() * 50); // Random coins between 0 and 50

    return {
      title: pub.title,
      values,
      xp,
      coins,
      topSdg,
      year: pub.year, // Assuming the publication has a `year` field
    };
  });
});
</script>
