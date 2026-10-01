<template>
  <div class="frame-container flex flex-col">
    <div class="flex-none flex items-center justify-between gap-2">
      <div class="frame-title !mb-2"><b>Browse & Compare:</b> Review Your Selected Publications in the <b>Publication Table</b></div>
      <span class="mb-2 font-mono text-[11px] text-fg-faint whitespace-nowrap">rows=<b class="text-accent">{{ sortedTableData.length }}</b></span>
    </div>
    <div>
      <UModal v-model="isOpen"  :overlay="false" :ui="{ width: 'w-full sm:max-w-4xl' }">
        <div
          v-if="selectedPublication">
          <PublicationDetails />
        </div>
      </UModal>
    </div>

    <div class="flex-1 min-h-0 max-h-[70vh] xl:max-h-none overflow-auto rounded-xl border border-line">
      <!-- Scrollable container -->
      <table
        class="pub-table"
        @mouseleave="publicationsStore.setHoveredPublication(null)"
      >
        <thead>
        <tr>
          <th
            v-for="column in tableColumns"
            :key="column.label"
            :class="[column.align === 'right' ? 'text-right' : 'text-left', { 'is-sortable': column.key, 'is-sorted': column.key && sortKey === column.key }]"
            :aria-sort="column.key && sortKey === column.key ? (sortOrder === 'asc' ? 'ascending' : 'descending') : undefined"
            @click="column.key && sortTable(column.key)"
          >
            <span class="inline-flex items-center gap-1">
              {{ column.label }}
              <template v-if="column.key">
                <Icon v-if="sortKey === column.key" :name="sortOrder === 'asc' ? 'mdi-chevron-up' : 'mdi-chevron-down'" class="h-3.5 w-3.5 text-accent" />
                <Icon v-else name="mdi-unfold-more-horizontal" class="h-3.5 w-3.5 opacity-40" />
              </template>
            </span>
          </th>
        </tr>
        </thead>
        <tbody>
        <tr v-if="sortedTableData.length === 0">
          <td :colspan="tableColumns.length" class="!py-10">
            <div class="flex flex-col items-center gap-2 text-center">
              <Icon name="mdi-lasso" class="h-7 w-7 text-accent" />
              <p class="font-mono text-xs text-fg-dim">No publications selected.</p>
              <p class="text-xs text-fg-faint">Draw a lasso around cells on the publication map to list them here.</p>
            </div>
          </td>
        </tr>
        <tr
          v-for="(item, index) in sortedTableData"
          :key="index"
          class="pub-table__row"
          :class="{ 'is-hovered': publicationsStore.hoveredPublication?.publicationId === item.publicationId }"
          :style="publicationsStore.hoveredPublication?.publicationId === item.publicationId ? { '--row-sdg': getSDGColor(item.topSDG) } : {}"
          @mouseover="publicationsStore.setHoveredPublication(item)"
          @mouseleave="publicationsStore.setHoveredPublication(null)">
          <td class="min-w-[12rem] max-w-[22rem]">
            <button type="button" class="pub-table__title" @click="handlePublicationClick(item)">
              {{ item.title }}
            </button>
          </td>
          <td>
            <!-- eslint-disable vue/no-v-html -- the SVG is built from numbers, colours and the scenario enum -->
            <div
              class="pub-table__symbol"
              v-html="generateHexagonSVG(Math.round(item.xp), getSDGColor(item.topSDG), getSDGColor(item.topSDG), item.scenarioType)"/>
            <!-- eslint-enable vue/no-v-html -->
          </td>
          <td>
            <div class="flex justify-center">
              <HexGlyph :key="item.publicationId + '-' + sortKey + '-' + sortOrder" :values="item.values" :height="56" :width="50" />
            </div>
          </td>
          <td>
            <BarPredictionPlot :values="item.values" :width="84" :height="48" />
          </td>
          <td>
            <div class="flex items-center gap-1.5">
              <img
                :src="getSDGIconSrc(item.topSDG)"
                :alt="item.topSDG"
                class="h-7 w-7 rounded-md object-contain"
              >
            </div>
          </td>
          <td class="text-right font-mono tabular-nums">{{ item.coins }}</td>
          <td class="text-right font-mono tabular-nums">{{ item.xp }}</td>
          <td class="text-right font-mono tabular-nums text-fg-dim">{{ item.year }}</td>
          <td>
            <UTooltip :text="item.collectionName">
              <Icon :name="item.collectionSymbol" class="h-5 w-5 text-fg-dim" />
            </UTooltip>
          </td>
          <td>
            <template v-if="item.scenarioType !== 'Not enough votes'">
              <QuestChip v-bind="getScenarioProps(item.scenarioType)" />
            </template>
            <template v-else>
              <span class="font-mono text-[11px] text-fg-faint">no quest</span>
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

// Columns of the table; `key` makes a column sortable
const tableColumns: { label: string; key?: string; align?: "right" }[] = [
  { label: "Title", key: "title" },
  { label: "Symbol" },
  { label: "Machine Scores" },
  { label: "Top SDGs" },
  { label: "Top SDG", key: "topSDGNumber" },
  { label: "Coins", key: "coins", align: "right" },
  { label: "XP", key: "xp", align: "right" },
  { label: "Year", key: "year", align: "right" },
  { label: "Topic", key: "collectionName" },
  { label: "Quest", key: "scenarioType" },
];

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
    large: { width: 60, height: 60, strokeWidth: 15 },
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
