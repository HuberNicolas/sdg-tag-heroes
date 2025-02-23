<template>
  <div class="frame-container">
    <div class="frame-title"><b>Scroll</b> through the selected Publications</div>

    <div>
      <UModal v-model="isOpen"  :overlay="false" :ui="{ width: 'w-full sm:max-w-4xl' }">
        <div
          v-if="selectedPublication">
          <PublicationDetails />
        </div>
      </UModal>
    </div>

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
          <th class="border border-gray-300 p-2">Symbol</th>
          <th class="border border-gray-300 p-2">Machine Scores</th>
          <th class="border border-gray-300 p-2">Top SDGs</th>
          <th
            @click="sortTable('topSDGNumber')"
            class="border border-gray-300 p-2 cursor-pointer hover:bg-gray-200 transition text-gray-600"
            :class="{ 'font-bold text-gray-800': sortKey === 'topSDGNumber' }"
          >
            Top SDG
            <span v-if="sortKey === 'topSDGNumber'">
              {{ sortOrder === 'asc' ? '▲' : '▼' }}
            </span>
            <span v-else class="text-gray-400">↕</span>
          </th>

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
            Quest
            <span v-if="sortKey === 'scenarioType'">
            {{ sortOrder === 'asc' ? '▲' : '▼' }}
          </span>
            <span v-else class="text-gray-400">↕</span>
          </th>
        </tr>
        </thead>
        <tbody>
        <tr v-if="sortedTableData.length === 0">
          <td colspan="8" class="border border-gray-300 p-4 text-center text-gray-500">
            No publications selected. Please use the lasso selection tool in the scatter plot to select data points.
          </td>
        </tr>
        <tr
          v-for="(item, index) in sortedTableData"
          :key="index"
          class="hover:bg-gray-50"
          @mouseover="publicationsStore.setHoveredPublication(item)"
          @mouseleave="publicationsStore.setHoveredPublication(null)"
          :style="{ backgroundColor: publicationsStore.hoveredPublication?.publicationId === item.publicationId ? getSDGColor(item.topSDG) : '' }">
          <td class="border border-gray-300 p-2 text-xs cursor-pointer hover:bg-gray-50"
              @click="handlePublicationClick(item)">
            {{ item.title }}
          </td>
          <td class="border border-gray-300 p-2">
            <div class="relative flex items-center justify-center"
                 v-html="generateHexagonSVG(Math.round(item.xp), getSDGColor(item.topSDG), getSDGColor(item.topSDG), item.scenarioType)">
            </div>
          </td>
          <td class="border border-gray-300 p-2 flex items-center justify-center">
            <HexGlyph :values="item.values" :height="80" :width="70" :key="item.publicationId + '-' + sortKey + '-' + sortOrder" />
          </td>
          <td class="border border-gray-300 p-2">
            <BarPredictionPlot :values="item.values" :width="80" :height="60" />
          </td>
          <td class="border border-gray-300 p-2">
            <div class="flex flex-col items-center justify-between h-full">
              <div class="w-8 h-8 flex items-center justify-center">
                <img
                  :src="getSDGIconSrc(item.topSDG)"
                  class="w-full h-full object-contain"
                />
              </div>
              <span class="text-center">{{ item.topSDGNumber }}</span>
            </div>
          </td>
          <td class="border border-gray-300 p-2">{{ item.coins }}</td>
          <td class="border border-gray-300 p-2">{{ item.xp }}</td>
          <td class="border border-gray-300 p-2">{{ item.year }}</td>
          <td class="border border-gray-300 p-2">
            <div class="flex items-center justify-center relative w-full h-full">
              <div class="relative group flex items-center">
                <Icon :name="item.collectionSymbol" class="w-8 h-8 text-gray-400" />

                <span
                  v-if="item.collectionName"
                  class="absolute right-full top-1/2 transform -translate-y-1/2 mr-2 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap"
                >
        {{ item.collectionName }}
      </span>
              </div>
            </div>
          </td>
          <td class="border border-gray-300 p-2">
            <template v-if="item.scenarioType !== 'Not enough votes'">
              <QuestChip v-bind="getScenarioProps(item.scenarioType)" />
            </template>
            <template v-else>
              No Quest
            </template>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";
import { usePublicationsStore } from '~/stores/publications';
import { useSDGPredictionsStore } from '~/stores/sdgPredictions';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useCollectionsStore} from "~/stores/collections";
import { useSDGsStore} from "~/stores/sdgs";
import HexGlyph from '@/components/PredictionGlyph.vue';
import BarPredictionPlot from "@/components/plots/BarPredictionPlot.vue";
import {score}from "@/utils/xp_scorer";
import type { PublicationSchemaBase } from "~/types/publication";
import PublicationDetails from "~/components/PublicationDetails.vue";

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
  'Scarce Labels': {
    icon: "i-heroicons-light-bulb",
    name: "Scarce Labels",
    tooltip: "Label an instance with the least labels"
  },
  'High Uncertainty': {
    icon: "i-heroicons-fire",
    name: "High Uncertainty",
    tooltip: "Sort the most uncertain instances based on entropy"
  },
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

      const decision = [...labelDecisionsStore.partitionedSDGLabelDecisions, ...labelDecisionsStore.scenarioTypeSDGLabelDecisions]
        .find(d => d.publicationId === pub.publicationId);

      const values = [
        prediction.sdg1, prediction.sdg2, prediction.sdg3, prediction.sdg4, prediction.sdg5,
        prediction.sdg6, prediction.sdg7, prediction.sdg8, prediction.sdg9, prediction.sdg10,
        prediction.sdg11, prediction.sdg12, prediction.sdg13, prediction.sdg14, prediction.sdg15,
        prediction.sdg16, prediction.sdg17
      ].filter(v => typeof v === 'number' && !isNaN(v));

      const P_max = values.length > 0 ? Math.max(...values) : 0.95;
      const N = Array.isArray(decision?.userLabels) ? decision.userLabels.length : 0;

      let coins = 0;
      try {
        coins = await score(N, P_max);
      } catch (error) {
        console.error("Error computing score:", error);
      }

      const collection = collectionsStore.collections.find(col => col.collectionId === pub.collectionId);
      const collectionName = pub.collectionName || collection?.shortName || 'Unknown Collection';
      const collectionSymbol = pub.collectionSymbol || (collection ? getIconComponent(collection.shortName) : 'mdi:help-circle');

      const scenarioType = decision?.scenarioType || 'No Scenario';

      return {
        title: pub.title,
        publicationId: pub.publicationId,
        values,
        xp: Math.round(prediction.entropy * 100),
        coins,
        topSDG: `SDG ${values.indexOf(P_max) + 1}`,
        topSDGNumber: values.indexOf(P_max) + 1,
        year: pub.year,
        scenarioType,
        collectionName,
        collectionSymbol
      };
    })
  );
  console.log(tableData);
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

const isOpen = ref(false)


function handlePublicationClick(publication: PublicationSchemaBase) {
  publicationsStore.setSelectedPublication(publication);
  this.isOpen = true;
}

const getSDGColor = (sdgName: string) => {
  if (!sdgName) return 'transparent'; // Default if no SDG
  const sdgId = parseInt(sdgName.replace('SDG ', ''), 10); // Extract SDG number
  return sdgsStore.getColorBySDG(sdgId) || 'transparent';
};

const getSDGIconSrc = (sdgName: string) => {
  if (!sdgName) return '';
  const sdgId = parseInt(sdgName.replace('SDG ', ''), 10); // Extract SDG number
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === sdgId);
  return sdg ? `data:image/svg+xml;base64,${sdg.icon}` : '';
};




// Get selected publication from the store
const selectedPublication = computed(() => publicationsStore.selectedPublication);

const generateHexagonSVG = (xpNormal: number, innerColor: string, outerColor: string, scenarioType: string) => {
  // Determine size based on xpNormal value
  let size = 'small';

  const maxXP = 800;  // Define the upper threshold for distribution
  const step = maxXP / 3;  // Divide into three equal ranges

  switch (true) {
    case xpNormal >= 2 * step: // 533 and above
      size = 'large';
      break;
    case xpNormal >= step: // 267 - 532
      size = 'medium';
      break;
    default: // 0 - 266
      size = 'small';
  }

  // Define dimensions based on size
  const dimensions = {
    small: { width: 20, height: 20, strokeWidth: 8 },
    medium: { width: 40, height: 40, strokeWidth: 10 },
    large: { width: 80, height: 80, strokeWidth: 12 },
  };

  const { width, height, strokeWidth } = dimensions[size];

  // If there's a scenario type, render as a diamond (rotated square)
  if (scenarioType && scenarioType !== 'Not enough votes') {
    return `
      <svg width="${width}" height="${height}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <rect
          x="25" y="25" width="50" height="50"
          fill="${innerColor}"
          transform="rotate(45 50 50)"
        />
        <rect
          x="25" y="25" width="50" height="50"
          stroke="${outerColor}"
          stroke-width="${strokeWidth}"
          fill="transparent"
          transform="rotate(45 50 50)"
        />
      </svg>
    `;
  }

  // Default hexagon rendering
  return `
    <svg width="${width}" height="${height}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <polygon
        points="50,2 95,25 95,75 50,98 5,75 5,25"
        fill="${innerColor}"
        transform="rotate(90 50 50)"
      />
      <polygon
        points="50,2 95,25 95,75 50,98 5,75 5,25"
        stroke="${outerColor}"
        stroke-width="${strokeWidth}"
        fill="transparent"
        transform="rotate(90 50 50)"
      />
    </svg>
  `;
};
</script>
