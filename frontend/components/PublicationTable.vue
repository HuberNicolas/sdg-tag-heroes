<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { usePublicationsStore } from '~/stores/publications';

interface Props {
  sdgId: number;
  levelId: number;
}

const props = defineProps<Props>();
const router = useRouter();

const publicationStore = usePublicationsStore();
const { publications } = storeToRefs(publicationStore);

// State for fetching and errors
const fetching = ref(false);
const error = ref<Error | null>(null);

// Fetch publications for the given SDG and Level
const loadPublications = async () => {
  fetching.value = true;
  error.value = null;

  try {
    // Flatten and retrieve publication IDs for the given SDG and Level
    const pubIds = Object.keys(
      publicationStore.publications[props.sdgId]?.[props.levelId] || {}
    ).map(Number);

    if (pubIds.length === 0) {
      console.warn('No publications to fetch for this level.');
      return;
    }

    // Fetch publications if not already cached
    await publicationStore.fetchPublicationsBatch(props.sdgId, props.levelId, pubIds);
  } catch (err) {
    error.value = err as Error;
    console.error('Error loading publications:', err);
  } finally {
    fetching.value = false;
  }
};

// Flatten and retrieve all publications for the given SDG and Level
const allPublications = computed(() => {
  return Object.values(
    publicationStore.publications[props.sdgId]?.[props.levelId] || {}
  );
});

// Table Columns
const columns = [
  { key: 'publication_id', label: 'ID', sortable: true },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'year', label: 'Year', sortable: true },
  { key: 'publisher', label: 'Publisher', sortable: false }
];

// Search Query
const q = ref('');

// Filtered Rows
const filteredRows = computed(() => {
  if (!q.value) {
    return allPublications.value;
  }
  return allPublications.value.filter((publication) => {
    return Object.values(publication).some((value) =>
      String(value || '').toLowerCase().includes(q.value.toLowerCase())
    );
  });
});

// Pagination
const page = ref(1);
const pageElements = 5;
const pageCount = computed(() => Math.ceil(filteredRows.value.length / pageElements));
const rows = computed(() => {
  const start = (page.value - 1) * pageElements;
  const end = start + pageElements;
  return filteredRows.value.slice(start, end);
});

// Selection and Expandable Rows
const selected = ref([]);
const expand = ref({
  openedRows: [],
  row: {},
});

// Handle Row Selection
function select(row) {
  const index = selected.value.findIndex((item) => item.publication_id === row.publication_id);
  console.log(row)
  if (index === -1) {
    selected.value.push(row);

    // Navigate to the route when a row is selected
    router.push({ name: 'publications-id', params: { id: row.publication_id } });
  } else {
    selected.value.splice(index, 1);
  }
}

// Load data when the component is mounted
onMounted(() => {
  loadPublications();
});
</script>

<template>
  <div>
    <!-- Search Input -->
    <div class="flex px-3 py-3.5 border-b border-gray-200 dark:border-gray-700">
      <UInput v-model="q" placeholder="Search publications..." />
    </div>

    <!-- Table -->
    <UTable
      :loading="fetching"
      :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: 'Loading...' }"
      :progress="{ color: 'primary', animation: 'carousel' }"
      :empty-state="{ icon: 'i-heroicons-circle-stack-20-solid', label: 'No items.' }"
      class="w-full"
      v-model="selected"
      v-model:expand="expand"
      :columns="columns"
      :rows="rows"
      @select="select"
    >
      <template #expand="{ row }">
        <div class="p-4">
          <pre>{{ row }}</pre>
        </div>
      </template>
    </UTable>

    <!-- Pagination -->
    <div class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700">
      <UPagination v-model="page" :page-count="pageCount" :total="filteredRows.length" />
    </div>
  </div>
</template>
