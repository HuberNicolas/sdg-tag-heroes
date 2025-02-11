<template>
  <div class="max-h-[600px] overflow-y-auto h-full">
    <!-- Scrollable container -->
    <table class="w-full border-collapse">
      <thead>
      <tr class="bg-gray-100">
        <th @click="sortTable('title')" class="border border-gray-300 p-2 cursor-pointer">Title</th>
        <th class="border border-gray-300 p-2">Glyph</th>
        <th class="border border-gray-300 p-2">Top SDGs</th>
        <th @click="sortTable('coins')" class="border border-gray-300 p-2 cursor-pointer">Coins</th>
        <th @click="sortTable('year')" class="border border-gray-300 p-2 cursor-pointer">Year</th>
        <th @click="sortTable('collectionName')" class="border border-gray-300 p-2 cursor-pointer">Collection</th>
        <th @click="sortTable('scenarioType')" class="border border-gray-300 p-2 cursor-pointer">Scenario</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(item, index) in sortedTableData" :key="index" class="hover:bg-gray-50">
        <td class="border border-gray-300 p-2 text-xs cursor-pointer hover:bg-gray-50"
            @click="handlePublicationClick(item)">
          {{ item.title }}
        </td>
        <td class="border border-gray-300 p-2 flex items-center justify-center">
          <HexGlyph :values="item.values" :height="80" :width="60" />
        </td>
        <td class="border border-gray-300 p-2">
          <BarPredictionPlot :values="item.values" :width="80" :height="60" />
        </td>
        <td class="border border-gray-300 p-2">{{ item.coins }}</td>
        <td class="border border-gray-300 p-2">{{ item.year }}</td>
        <td class="border border-gray-300 p-2 flex flex-auto justify-evenly content-center">
          <UTooltip :text="item.collectionName">
            <Icon :name="item.collectionSymbol" class="w-8 h-8 text-gray-400" />
          </UTooltip>
        </td>
        <td v-if="item.scenarioType">
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
import { useCollectionsStore} from "~/stores/collections";
import HexGlyph from '@/components/PredictionGlyph.vue';
import BarPredictionPlot from "@/components/plots/BarPredictionPlot.vue";

const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const labelDecisionsStore = useLabelDecisionsStore();
const collectionsStore = useCollectionsStore();


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

// Map collection names to corresponding icons
const iconMapping = {
  'Cancer Imaging': 'mdi:radiology-box',
  'Heart Imaging': 'mdi:heart-box',
  'Swiss Research': 'twemoji:flag-switzerland',
  'Cell Signaling': 'mdi:signal',
  'Mental Health': 'mdi:meditation',
  'Brain Function': 'mdi:head-cog',
  'Ecosystem Changes': 'material-symbols:nature',
  'Pandemic Studies': 'fa-solid:virus',
  'Sustainability Policies': 'carbon:sustainability',
  'Particle Physics': 'ion:planet',
  'Molecular Chemistry': 'material-symbols:science',
  'Dental Implants': 'mdi:tooth',
  'Financial Models': 'fa-solid:chart-line',
  'Bacterial Resistance': 'mdi:bacteria',
  'Data Processing': 'icon-park-outline:data',
  'Mathematical Models': 'mdi:math-compass',
  'Neural Networks': 'mdi:brain',
  'Environmental Sensing': 'mdi:leaf',
  'Tech Governance': 'mdi:shield-account',
  'Genetic Mutations': 'mdi:dna',
  'Material Science': 'mdi:flask',
};

// Function to get the corresponding icon component for each collection name
const getIconComponent = (name: string) => {
  return iconMapping[name] || 'mdi:help-circle'
};



// Map selected publications and predictions to table data
const tableData = computed(() => {
  return publicationsStore.selectedPartitionedPublications.map((pub, index) => {
    const prediction = sdgPredictionsStore.selectedPartitionedSDGPredictions[index];

    const decision = [...labelDecisionsStore.sdgLevelSDGLabelDecisions, ...labelDecisionsStore.scenarioTypeSDGLabelDecisions]
      .find(d => d.publicationId === pub.publicationId);

    const values = [
      prediction.sdg1, prediction.sdg2, prediction.sdg3, prediction.sdg4, prediction.sdg5,
      prediction.sdg6, prediction.sdg7, prediction.sdg8, prediction.sdg9, prediction.sdg10,
      prediction.sdg11, prediction.sdg12, prediction.sdg13, prediction.sdg14, prediction.sdg15,
      prediction.sdg16, prediction.sdg17
    ];

    const sdgKeys = Array.from({ length: 17 }, (_, i) => `sdg${i + 1}`);
    const topSdgKey = sdgKeys.reduce((a, b) => prediction[a] > prediction[b] ? a : b);
    const topSdg = `SDG ${topSdgKey.replace('sdg', '')}`;

    const coins = Math.round(prediction.entropy * 100);

    // Fetch the collection name and symbol (assuming collectionId is available)
    const collection = collectionsStore.collections.find(col => col.collectionId === pub.collectionId);
    const collectionName = collection ? collection.shortName : 'Unknown Collection';
    const collectionSymbol = collection ? getIconComponent(collection.shortName) : '';

    return {
      title: pub.title,
      publicationId: pub.publicationId,
      values,
      coins,
      topSdg,
      year: pub.year,
      scenarioType: decision?.scenarioType || null,
      collectionName,
      collectionSymbol
    };
  });
});

const sortKey = ref('title');
const sortOrder = ref('asc');

const sortTable = (key: string) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'asc';
  }
};

const sortedTableData = computed(() => {
  return [...tableData.value].sort((a, b) => {
    let result = 0;
    if (a[sortKey.value] < b[sortKey.value]) result = -1;
    if (a[sortKey.value] > b[sortKey.value]) result = 1;
    return sortOrder.value === 'asc' ? result : -result;
  });
});

function handlePublicationClick(publication: PublicationSchemaBase) {
  publicationsStore.setSelectedPublication(publication);
}
</script>
