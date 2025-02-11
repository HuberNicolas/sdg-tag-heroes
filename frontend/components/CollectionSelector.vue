<template>
  <div>
    <!-- Selected filter badges summary -->
    <div class="flex items-center gap-3">

      <div class="flex items-center gap-3">
        <div class="flex gap-2">
          <button
            @click="resetSelection"
            class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Reset
          </button>
          <button
            @click="selectAllCollections"
            class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
          >
            Select All
          </button>
        </div>
      </div>

      <!-- Select menu for icons -->
      <USelectMenu
        v-model="selectedCollections"
        @update:modelValue="updateSelectedCollections"
        by="name"
        name="collections"
        :options="collections"
        option-attribute="shortName"
        multiple
        searchable
        creatable
        class="flex-1"
      >
        <template #label>
        <span v-if="selectedCollections.length">
          {{ selectedCollections.length }} Collection{{ selectedCollections.length > 1 ? 's' : '' }}
        </span>
          <span v-else class="text-gray-500">
          Select Collection
        </span>
        </template>

        <template #option="{ option }">
          <div class="flex items-center">
            <component :is="getIconComponent(option.shortName)" class="mr-2 text-xl" />
            <span class="truncate">{{ option.shortName }}</span>
          </div>
        </template>

        <template #option-create="{ option }">
          <div class="flex items-center">
            <span>New Collection: </span>
            <component :is="getIconComponent(option.shortName)" class="mr-2 text-xl" />
            <span class="truncate">{{ option.shortName }}</span>
          </div>
        </template>
      </USelectMenu>
    </div>

    <div class="mb-1">
      <div class="flex flex-wrap gap-1">
        <UBadge
          v-for="(collection, index) in selectedCollections"
          :key="index"
          :icon="getIconComponent(collection.shortName)"
          size="sm"
          color="primary"
          variant="solid"
          class="flex items-center gap-1 px-1 py-1"
        >
          <span class="truncate">{{ collection.shortName }}</span>
          <button @click.stop="removeCollection(collection)" class="ml-1">
            <UIcon name="i-heroicons-x-circle" class="w-2 h-4 text-white hover:text-gray-300" />
          </button>
        </UBadge>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCollectionsStore } from '~/stores/collections'

// Access store
const collectionsStore = useCollectionsStore();
const collections = ref([]);
const selectedCollections = ref([]);



// Fetch collections on mount
onMounted(async () => {
  await collectionsStore.fetchCollections();
  collections.value = collectionsStore.collections;
  selectedCollections.value = [...collectionsStore.selectedCollections]; // Keep selection in sync
});

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

const removeCollection = (collectionToRemove) => {
  collectionsStore.setSelectedCollections(
    collectionsStore.selectedCollections.filter(
      (collection) => collection.collectionId !== collectionToRemove.collectionId
    )
  );
  selectedCollections.value = [...collectionsStore.selectedCollections]; // Update the UI
};

const updateSelectedCollections = (newSelection) => {
  collectionsStore.setSelectedCollections(newSelection);
  selectedCollections.value = [...collectionsStore.selectedCollections];
};

// Function to reset selected collections
const resetSelection = () => {
  selectedCollections.value = [];
  collectionsStore.setSelectedCollections([]);
};

// Function to select all collections
const selectAllCollections = () => {
  selectedCollections.value = [...collections.value];
  collectionsStore.setSelectedCollections(selectedCollections.value);
};


</script>
