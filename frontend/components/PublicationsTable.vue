<template>
  <div class="max-h-[600px] overflow-y-auto h-full">
    <!-- Scrollable container -->
    <table
      class="w-full border-collapse"
      @mouseleave="publicationsStore.setHoveredPublication(null)"
    >
      <thead>
      <tr class="bg-gray-100">
        <th
          @click="sortTable('title')"
          class="border border-gray-300 p-2 cursor-pointer hover:bg-gray-200 transition text-gray-600"
          :class="{ 'font-bold text-gray-800': sortKey === 'title' }"
        >
          Title
          <span v-if="sortKey === 'title'">
              {{ sortOrder === 'asc' ? '▲' : '▼' }}
            </span>
          <span v-else class="text-gray-400">↕</span>
        </th>
        <th class="border border-gray-300 p-2">Glyph</th>
        <th class="border border-gray-300 p-2">Top SDGs</th>

        <th @click="sortTable('coins')"
            class="border border-gray-300 p-2 sortable-header"
            :class="{ 'active-sort': sortKey === 'coins' }">
          Coins
          <span v-if="sortKey === 'coins'">
            {{ sortOrder === 'asc' ? '▲' : '▼' }}
          </span>
          <span v-else class="text-gray-400">↕</span>
        </th>

        <th @click="sortTable('xp')"
            class="border border-gray-300 p-2 sortable-header"
            :class="{ 'active-sort': sortKey === 'xp' }">
          XP
          <span v-if="sortKey === 'xp'">
            {{ sortOrder === 'asc' ? '▲' : '▼' }}
          </span>
          <span v-else class="text-gray-400">↕</span>
        </th>

        <th @click="sortTable('year')"
            class="border border-gray-300 p-2 sortable-header"
            :class="{ 'active-sort': sortKey === 'year' }">
          Year
          <span v-if="sortKey === 'year'">
            {{ sortOrder === 'asc' ? '▲' : '▼' }}
          </span>
          <span v-else class="text-gray-400">↕</span>
        </th>
        <th @click="sortTable('collectionName')"
            class="border border-gray-300 p-2 sortable-header"
            :class="{ 'active-sort': sortKey === 'collectionName' }">
          Topic
          <span v-if="sortKey === 'collectionName'">
            {{ sortOrder === 'asc' ? '▲' : '▼' }}
          </span>
          <span v-else class="text-gray-400">↕</span>
        </th>

        <th @click="sortTable('scenarioType')"
            class="border border-gray-300 p-2 sortable-header"
            :class="{ 'active-sort': sortKey === 'scenarioType' }">
          Scenario
          <span v-if="sortKey === 'scenarioType'">
            {{ sortOrder === 'asc' ? '▲' : '▼' }}
          </span>
          <span v-else class="text-gray-400">↕</span>
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-if="sortedTableData.length === 0">
        <td colspan="7" class="border border-gray-300 p-4 text-center text-gray-500">
          No publications selected. Please use the lasso selection tool in the scatter plot to select data points.
        </td>
      </tr>
      <tr
        v-for="(item, index) in sortedTableData"
        :key="index"
        class="hover:bg-gray-50"
        @mouseover="publicationsStore.setHoveredPublication(item)"
        @mouseleave="publicationsStore.setHoveredPublication(null)"
        :style="{ backgroundColor: publicationsStore.hoveredPublication?.publicationId === item.publicationId ? getSDGColor(item.topSdg) : '' }">

        <td class="border border-gray-300 p-2 text-xs cursor-pointer hover:bg-gray-50"
            @click="handlePublicationClick(item)">
          {{ item.title }}
        </td>
        <td class="border border-gray-300 p-2 flex items-center justify-center">
          <HexGlyph :values="item.values" :height="80" :width="70" :key="item.publicationId + '-' + sortKey + '-' + sortOrder" />
        </td>
        <td class="border border-gray-300 p-2">
          <BarPredictionPlot :values="item.values" :width="80" :height="60" />
        </td>
        <td class="border border-gray-300 p-2">{{ item.coins }}</td>
        <td class="border border-gray-300 p-2">{{ item.xp }}</td>
        <td class="border border-gray-300 p-2">{{ item.year }}</td>
        <td class="border border-gray-300 p-2 flex flex-auto justify-evenly content-center">
          <UTooltip :text="item.collectionName">
            <Icon :name="item.collectionSymbol" class="w-8 h-8 text-gray-400" />
          </UTooltip>
        </td>

        <td class="border border-gray-300 p-2">
          <template v-if="item.scenarioType !== 'No Scenario'">
            <QuestChip v-bind="getScenarioProps(item.scenarioType)" />
          </template>
          <template v-else>
            No Scenario
          </template>
        </td>

      </tr>
      </tbody>
    </table>
  </div>
</template>


<script setup lang="ts">
import { computed, watch, watchEffect } from 'vue';
import { usePublicationsStore } from '~/stores/publications';
import { useSDGPredictionsStore } from '~/stores/sdgPredictions';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useCollectionsStore} from "~/stores/collections";
import { useSDGsStore} from "~/stores/sdgs";
import HexGlyph from '@/components/PredictionGlyph.vue';
import BarPredictionPlot from "@/components/plots/BarPredictionPlot.vue";
import {score}from "@/utils/xp_scorer";

const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const labelDecisionsStore = useLabelDecisionsStore();
const collectionsStore = useCollectionsStore();
const sdgsStore = useSDGsStore();

const sortKey = ref('title');
const sortOrder = ref('asc');
const tableData = ref([]); // Store resolved data
const sortedTableData = ref([]); // Store sorted data


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
  'Investigate': {
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
  "Swiss Research": "gg:swiss",
  'Cell Signaling': 'mdi:bio',
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


// Load & Watch for changes in table data
watchEffect(async () => {
  tableData.value = await Promise.all(
    publicationsStore.selectedPartitionedPublications.map(async (pub, index) => {
      const prediction = sdgPredictionsStore.selectedPartitionedSDGPredictions[index];

      const decision = [...labelDecisionsStore.sdgLevelSDGLabelDecisions, ...labelDecisionsStore.scenarioTypeSDGLabelDecisions]
        .find(d => d.publicationId === pub.publicationId);

      const values = [
        prediction.sdg1, prediction.sdg2, prediction.sdg3, prediction.sdg4, prediction.sdg5,
        prediction.sdg6, prediction.sdg7, prediction.sdg8, prediction.sdg9, prediction.sdg10,
        prediction.sdg11, prediction.sdg12, prediction.sdg13, prediction.sdg14, prediction.sdg15,
        prediction.sdg16, prediction.sdg17
      ].filter(v => typeof v === 'number' && !isNaN(v));

      const P_max = values.length > 0 ? Math.max(...values) : 0.95;
      const N = Array.isArray(decision?.userLabels) ? decision.userLabels.length : 0;

      let xp = 0;
      try {
        xp = await score(N, P_max);
      } catch (error) {
        console.error("Error computing score:", error);
      }

      const collection = collectionsStore.collections.find(col => col.collectionId === pub.collectionId);
      const collectionName = collection?.shortName || 'Unknown Collection';
      const collectionSymbol = collection ? getIconComponent(collection.shortName) : 'mdi:help-circle';

      const scenarioType = decision?.scenarioType || 'No Scenario';

      return {
        title: pub.title,
        publicationId: pub.publicationId,
        values,
        coins: Math.round(prediction.entropy * 100),
        xp,
        topSdg: `SDG ${values.indexOf(P_max) + 1}`,
        year: pub.year,
        scenarioType,
        collectionName,
        collectionSymbol
      };
    })
  );

  // Initial sort after loading
  sortTable(sortKey.value);
});


const sortTable = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'asc';
  }

  // Perform sorting
  sortedTableData.value = [...tableData.value].sort((a, b) => {
    let result = 0;
    if (a[key] < b[key]) result = -1;
    if (a[key] > b[key]) result = 1;
    return sortOrder.value === 'asc' ? result : -result;
  });
};



function handlePublicationClick(publication: PublicationSchemaBase) {
  publicationsStore.setSelectedPublication(publication);
}

const getSDGColor = (sdgName: string) => {
  if (!sdgName) return 'transparent'; // Default if no SDG
  const sdgId = parseInt(sdgName.replace('SDG ', ''), 10); // Extract SDG number
  return sdgsStore.getColorBySDG(sdgId) || 'transparent';
};

</script>
