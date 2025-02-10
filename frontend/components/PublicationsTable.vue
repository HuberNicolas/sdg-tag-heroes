<template>
  <div class="overflow-auto h-full">
    <!-- Scrollable container -->
    <table class="w-full border-collapse">
      <thead>
      <tr class="bg-gray-100">
        <th class="border border-gray-300 p-2">Title</th>
        <th class="border border-gray-300 p-2">Glyph</th>
        <th class="border border-gray-300 p-2">Top SDGs</th>
        <!--<th class="border border-gray-300 p-2">XP</th>--->
        <th class="border border-gray-300 p-2">Coins</th>
        <th class="border border-gray-300 p-2">Year</th>
        <th class="border border-gray-300 p-2">Scenario</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(item, index) in tableData" :key="index" class="hover:bg-gray-50">
        <td class="border border-gray-300 p-2 text-xs">
          <NuxtLink :to="`/labeling2/${item.publicationId}`">{{ item.title }}</NuxtLink>
        </td>
        <td class="border border-gray-300 p-2 flex items-center justify-center">
          <HexGlyph :values="item.values" :height="80" :width="60" />
        </td>
        <td class="border border-gray-300 p-2">
          <BarPredictionPlot :values="item.values" :width="80" :height="60" />
        </td>
        <!--<td class="border border-gray-300 p-2">{{ item.xp }}</td>--->
        <td class="border border-gray-300 p-2">{{ item.coins }}</td>
        <td class="border border-gray-300 p-2">{{ item.year }}</td>
        <td v-if="item.scenarioType">
          <!-- Render the ScenarioChip with mapped props -->
          <QuestChip v-bind="getScenarioProps(item.scenarioType)" />
        </td>
        <td v-else>
          No Scenario
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import { usePublicationsStore } from '~/stores/publications';
import { useSDGPredictionsStore } from '~/stores/sdgPredictions';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import HexGlyph from '@/components/PredictionGlyph.vue';
import BarPredictionPlot from "@/components/plots/BarPredictionPlot.vue";

const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const labelDecisionsStore = useLabelDecisionsStore();


watch(
  () => labelDecisionsStore.scenarioTypeSDGLabelDecisions,
  (newVal) => {
    console.log("Scenario Label Decisions Updated:", newVal);
  },
  { deep: true }
);


function getScenarioProps(scenarioType: string) {
  // Return the mapping or a fallback if not found
  return scenarioMapping[scenarioType] || { icon: '', name: '', tooltip: '' };
}

// Mapping for scenario types to chip properties
const scenarioMapping: Record<string, { icon: string; name: string; tooltip: string }> = {
  'Confirm': {
    icon: 'i-heroicons-check-badge',
    name: 'Confirm the King',
    tooltip: 'Crown the most prominent instance'
  },
  'Explore': {
    icon: 'i-heroicons-map',
    name: 'Explore',
    tooltip: 'Look at a variety of predictions to explore uncertainty'
  },
  'Investment': {
    icon: 'i-heroicons-magnifying-glass',
    name: 'Investigate',
    tooltip: 'Analyze and investigate data'
  },
  'Tiebreaker': {
    icon: 'i-heroicons-scale',
    name: 'Tiebreaker',
    tooltip: 'Resolve conflicts with a balanced approach'
  },
  'Not enough votes': {
    icon: 'question-mark-circle',
    name: 'Not enough votes',
    tooltip: 'Not enough votes'
  },
  'Decided': {
    icon: 'check-mark-circle',
    name: 'Decided',
    tooltip: 'Decided'
  }
};


// Map selected publications and predictions to table data
const tableData = computed(() => {
  return publicationsStore.selectedPartitionedPublications.map((pub, index) => {
    const prediction = sdgPredictionsStore.selectedPartitionedSDGPredictions[index];

    // Find decision in either standard or scenario-based SDG decisions
    const decision = [...labelDecisionsStore.sdgLevelSDGLabelDecisions, ...labelDecisionsStore.scenarioTypeSDGLabelDecisions]
      .find(d => d.publicationId === pub.publicationId);


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
    //const xp = Math.round(prediction.entropy*100)
    const coins = Math.round(prediction.entropy*100)

    return {
      title: pub.title,
      publicationId: pub.publicationId,
      values,
      //xp,
      coins,
      topSdg,
      year: pub.year, // Assuming the publication has a `year` field
      scenarioType: decision?.scenarioType || null
    };
  });
});
</script>
