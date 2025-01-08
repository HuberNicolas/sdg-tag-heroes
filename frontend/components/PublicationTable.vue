<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { usePublicationsStore } from '~/stores/publications';

interface Props {
  sdgId: number;
  levelId: number;
}

const props = defineProps<Props>();
const router = useRouter();

const publicationStore = usePublicationsStore();

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

// Handle Row Selection
function select(publication) {
  router.push({ name: 'publications-id', params: { id: publication.publication_id } });
}

// Load data when the component is mounted
onMounted(() => {
  loadPublications();
});
</script>


<template>
  <div>
    <!-- Search Input -->
    <div class="flex px-4 py-3 border-b border-gray-200 bg-gray-50">
      <input
        v-model="q"
        type="text"
        class="w-full px-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring focus:ring-indigo-500"
        placeholder="Search publications..."
      />
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full bg-white border border-gray-200">
        <thead class="bg-gray-100">
        <tr>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">ID</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Title</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Year</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Publisher</th>
        </tr>
        </thead>
        <tbody>
        <tr
          v-for="publication in rows"
          :key="publication.publication_id"
          class="hover:bg-gray-50 cursor-pointer"
          @click="select(publication)"
        >
          <td class="px-4 py-2 text-sm text-gray-700">{{ publication.publication_id }}</td>
          <td class="px-4 py-2 text-sm text-gray-700">{{ publication.title }}</td>
          <td class="px-4 py-2 text-sm text-gray-700">{{ publication.year }}</td>
          <td class="px-4 py-2 text-sm text-gray-700">{{ publication.publisher }}</td>
        </tr>
        <tr v-if="!rows.length">
          <td colspan="4" class="px-4 py-2 text-sm text-center text-gray-500">No items found.</td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex justify-between items-center px-4 py-3 bg-gray-50 border-t border-gray-200">
      <p class="text-sm text-gray-500">
        Showing {{ (page - 1) * pageElements + 1 }} -
        {{ Math.min(page * pageElements, filteredRows.length) }} of {{ filteredRows.length }}
      </p>
      <div class="flex space-x-2">
        <button
          :disabled="page === 1"
          @click="page--"
          class="px-3 py-1 text-sm text-gray-700 bg-gray-100 border rounded hover:bg-gray-200 disabled:opacity-50"
        >
          Previous
        </button>
        <button
          :disabled="page === pageCount"
          @click="page++"
          class="px-3 py-1 text-sm text-gray-700 bg-gray-100 border rounded hover:bg-gray-200 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>
