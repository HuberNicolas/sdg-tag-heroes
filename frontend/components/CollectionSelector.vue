<template>
  <div class="frame-container">
    <div class="frame-title"><b>Select</b> Topics you are interested to find interesting publications from the <b> Topic List</b></div>
    <!-- Selected filter badges summary -->
    <div class="flex items-center gap-4">

      <div class="flex items-center gap-4">
        <div class="flex gap-2 p-2">
          <!-- Reset Button -->
          <UButton
            icon="i-heroicons-arrow-path"
            @click="resetSelection"
            :color="'primary'"
            :variant="'solid'"
          >
            Reset
          </UButton>

          <!-- Select All Button -->
          <UButton
            icon="i-heroicons-check-circle"
            @click="selectAllCollections"
            :color="'primary'"
            :variant="'solid'"
          >
            Select All
          </UButton>
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
          {{ selectedCollections.length }} Topic{{ selectedCollections.length > 1 ? "s" : "" }}
          ({{ selectedCollections.reduce((sum, col) => sum + (collectionsStore.collectionsCount[col.collectionId] || 0), 0)
          }} Publications)
        </span>
          <span v-else class="text-gray-500">
          Select Topics
        </span>
        </template>

        <template #option="{ option }">
          <div class="flex items-center justify-between w-full">
            <div class="flex items-center">
              <component :is="getIconComponent(option.shortName)" class="mr-2 text-xl" />
              <span>{{ option.shortName }}</span>
            </div>
            <span class="text-gray-500 text-sm"> ({{ collectionsStore.collectionsCount[option.collectionId] || 0 }} Publications) </span>
          </div>
        </template>


        <template #option-create="{ option }">
          <div class="flex items-center justify-between w-full">
            <div class="flex items-center">
              <span>New Topic:</span>
              <component :is="getIconComponent(option.shortName)" class="mr-2 text-xl" />
              <span>{{ option.shortName }}</span>
            </div>
            <span class="text-gray-500 text-sm"></span>
          </div>
        </template>

      </USelectMenu>
    </div>

    <div class="">
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
          <span class="truncate">{{ collection.shortName
            }} ({{ collectionsStore.collectionsCount[collection.collectionId] || 0 }}) </span>
          <button @click.stop="removeCollection(collection)" class="ml-1">
            <UIcon name="i-heroicons-x-circle" class="w-2 h-4 text-white hover:text-gray-300" />
          </button>
        </UBadge>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useCollectionsStore } from "~/stores/collections";

// Access store
const collectionsStore = useCollectionsStore();
const collections = ref([]);
const selectedCollections = ref([]);


// Watch for changes in the selectedCollections array
watch(selectedCollections, (newSelectedCollections) => {
  // Update the store whenever the selected collections change
  collectionsStore.setSelectedCollections(newSelectedCollections);
});


// Fetch collections on mount
onMounted(async () => {
  await collectionsStore.fetchCollections();
  collections.value = collectionsStore.collections;
  selectedCollections.value = [...collectionsStore.selectedCollections]; // Keep selection in sync
});

// Map collection names to corresponding icons
const iconMapping = {
  "Cancer Imaging": "mdi:radiology-box",
  "Heart Imaging": "mdi:heart-box",
  "Swiss Research": "gg:swiss",
  "Cell Signaling": "mdi:bio",
  "Mental Health": "mdi:meditation",
  "Brain Function": "mdi:head-cog",
  "Ecosystem Changes": "material-symbols:nature",
  "Pandemic Studies": "fa-solid:virus",
  "Sustainability Policies": "carbon:sustainability",
  "Particle Physics": "ion:planet",
  "Molecular Chemistry": "material-symbols:science",
  "Dental Implants": "mdi:tooth",
  "Financial Models": "fa-solid:chart-line",
  "Bacterial Resistance": "mdi:bacteria",
  "Data Processing": "icon-park-outline:data",
  "Mathematical Models": "mdi:math-compass",
  "Neural Networks": "mdi:brain",
  "Environmental Sensing": "mdi:leaf",
  "Tech Governance": "mdi:shield-account",
  "Genetic Mutations": "mdi:dna",
  "Material Science": "mdi:flask"
};

// Function to get the corresponding icon component for each collection name
const getIconComponent = (name: string) => {
  return iconMapping[name] || "mdi:help-circle";
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
