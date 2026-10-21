<template>
  <div class="frame-container flex flex-col">
    <div class="frame-title"><b>by choosing</b> research <b>topics</b> from the list</div>

    <div class="flex items-center gap-2">
      <!-- Select menu for icons -->
      <USelectMenu
        v-model="selectedCollections"
        by="name"
        name="collections"
        :options="collections"
        option-attribute="shortName"
        multiple
        searchable
        creatable
        class="flex-1 min-w-0"
        @update:model-value="updateSelectedCollections"
      >
        <template #label>
          <span v-if="selectedCollections.length" class="truncate font-mono text-xs">
            <b class="text-accent">{{ selectedCollections.length }}</b> topic{{ selectedCollections.length > 1 ? "s" : "" }}
            · <b class="text-accent">{{ selectedCollections.reduce((sum, col) => sum + (collectionsStore.collectionsCount[col.collectionId] || 0), 0) }}</b> publications
          </span>
          <span v-else class="truncate text-fg-dim">
            Select Topics to Discover Relevant Publications from the List
          </span>
        </template>

        <template #option="{ option }">
          <div class="flex items-center justify-between gap-3 w-full">
            <span class="flex items-center gap-2 min-w-0">
              <Icon :name="topicIcon(option.shortName)" class="h-4 w-4 flex-none text-fg-dim" />
              <span class="truncate">{{ option.shortName }}</span>
            </span>
            <span class="font-mono text-[11px] text-fg-faint">{{ collectionsStore.collectionsCount[option.collectionId] || 0 }}</span>
          </div>
        </template>

        <template #option-create="{ option }">
          <div class="flex items-center gap-2 w-full">
            <span class="font-mono text-[11px] text-fg-faint">new topic:</span>
            <span>{{ option.shortName }}</span>
          </div>
        </template>
      </USelectMenu>

      <!-- Reset Button -->
      <UButton
        icon="i-heroicons-arrow-path"
        color="gray"
        variant="soft"
        square
        title="Reset to all topics"
        aria-label="Reset to all topics"
        @click="resetSelection"
      />
    </div>

    <!-- Selected topics -->
    <div v-if="selectedCollections.length" class="mt-2 flex flex-wrap gap-1.5 max-h-20 overflow-y-auto">
      <span
        v-for="(collection, index) in selectedCollections"
        :key="index"
        class="topic-chip"
      >
        <Icon :name="topicIcon(collection.shortName)" class="h-3.5 w-3.5 flex-none text-accent" />
        <span class="truncate">{{ collection.shortName }}</span>
        <span class="font-mono text-[10px] text-fg-faint">{{ collectionsStore.collectionsCount[collection.collectionId] || 0 }}</span>
        <button type="button" class="topic-chip__remove" :aria-label="`Remove ${collection.shortName}`" @click.stop="removeCollection(collection)">
          <UIcon name="i-heroicons-x-mark" class="h-3 w-3" />
        </button>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useCollectionsStore } from "~/stores/collections";
import { topicIcon } from "~/utils/topicIcon";

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

  // Wait for collectionsCount to be available
  await new Promise((resolve) => {
    const checkCollectionsCount = () => {
      if (Object.keys(collectionsStore.collectionsCount).length) {
        resolve(true);
      } else {
        setTimeout(checkCollectionsCount, 100);
      }
    };
    checkCollectionsCount();
  });

  // Filter collections based on publication count
  collections.value = collectionsStore.collections.filter(
    (collection) => (collectionsStore.collectionsCount[collection.collectionId] || 0) > 0
  );

  selectedCollections.value = collectionsStore.selectedCollections.filter(
    (collection) => (collectionsStore.collectionsCount[collection.collectionId] || 0) > 0
  );

  // Start with all topics, so the map is not empty before the first filter is chosen
  selectAllCollections();
});


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

// Reset: back to all topics (the start state)
const resetSelection = () => {
  selectAllCollections();
};

// Function to select all collections
function selectAllCollections() {
  selectedCollections.value = collections.value.filter(
    (collection) => collectionsStore.collectionsCount[collection.collectionId] > 0
  );
  collectionsStore.setSelectedCollections(selectedCollections.value);
}


</script>

<style scoped>
.topic-chip {
  @apply inline-flex max-w-full items-center gap-1.5 rounded-full border border-line bg-surface-2/80 py-0.5 pl-2 pr-1 text-xs text-fg;
}
.topic-chip__remove {
  @apply grid h-4 w-4 place-items-center rounded-full text-fg-faint transition-colors hover:bg-hero-red/15 hover:text-hero-red;
}
</style>
