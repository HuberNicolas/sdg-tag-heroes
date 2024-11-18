<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref, computed, watch } from 'vue';
import { usePublicationStore } from '~/stores/publications';

const publicationStore = usePublicationStore();
const { publications } = storeToRefs(publicationStore);

// Watch the publications for changes (for debugging purposes)
watch(publications, () => {
  console.log(publications.value); // Check the structure of publications
});

// Extract and flatten the list of publications from the nested structure
const allPublications = computed(() => {
  const pubData = publications.value ? publications.value : {};
  // Flatten all the SDG publication arrays into a single array
  return Object.values(pubData).flat();
});
console.log(allPublications);

// Define columns for the UTable component
const columns = [
  { key: 'publication_id', label: 'ID', sortable: true },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'year', label: 'Year', sortable: true },
  { key: 'publisher', label: 'Publisher', sortable: false }
];

// Selection
const selected = ref([]);

// Search
const q = ref('');

// Filtered rows with search
const filteredRows = computed(() => {
  if (!q.value) {
    return allPublications.value;
  }

  return allPublications.value.filter((publication) => {
    return Object.values(publication).some((value) => {
      if (value) {
        return String(value).toLowerCase().includes(q.value.toLowerCase());
      }
      return false;
    });
  });
});


// Pagination
const pageElements = 5;
const page = ref(1);
const pageCount = computed(() => Math.ceil(filteredRows.value.length / pageElements));
const rows = computed(() => {
  const start = (page.value - 1) * pageElements;
  const end = start + pageElements;
  return filteredRows.value.slice(start, end); // `filteredRows.value` should always be an array now
});

// Expandable
const expand = ref({
  openedRows: [],
  row: {}
});

// Selection function
function select(row) {
  const index = selected.value.findIndex((item) => item.publication_id === row.publication_id);
  if (index === -1) {
    selected.value.push(row);
  } else {
    selected.value.splice(index, 1);
  }
}
</script>

<template>
  <div>
    <div class="flex px-3 py-3.5 border-b border-gray-200 dark:border-gray-700">
      <UInput v-model="q" placeholder="Filter publications..." />
    </div>

    <!-- Conditional Rendering: Check if publications are available -->
    <UTable
      :loading="publicationStore.loading"
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

    <div class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700">
      <UPagination v-model="page" :page-count="pageCount" :total="filteredRows.length" />
    </div>
  </div>
</template>
