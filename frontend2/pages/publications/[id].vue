<template>
  <div class="publication-details-page">
    <header class="flex justify-between items-start">
      <h1 class="text-2xl font-bold">Publication Glyph</h1>

      <!-- HexGrid Card at the Top Right -->
      <div class="w-1/3">
        <UCard
          class="aspect-square flex flex-col items-center justify-between text-center shadow-lg rounded-lg overflow-hidden"
          style="width: 100%; height: auto;"
        >
        <template #header>
          <h2 class="text-lg font-bold">Sustainable Goals Fingerprint</h2>
        </template>
        <HexGrid />
        <template #footer>
          <p class="text-sm mt-0">---</p>
        </template>
        </UCard>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-grow mt-6">
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="loading" class="loading">Loading publication details...</div>

      <div v-if="publication && !loading" class="publication-details">
        <h2 class="text-xl font-bold">{{ publication.title }}</h2>
        <p><strong>OAI Identifier:</strong> {{ publication.oai_identifier }}</p>
        <p><strong>OAI Identifier Num:</strong> {{ publication.oai_identifier_num }}</p>
        <p><strong>Description:</strong> {{ publication.description || "No description available." }}</p>

        <h3 class="font-semibold mt-4">Authors</h3>
        <ul v-if="publication.authors && publication.authors.length > 0">
          <li v-for="author in publication.authors" :key="author.author_id">
            <p>
              <strong>{{ formatAuthorName(author) }}</strong>
              <span v-if="author.orcid_id"> - ORCID: {{ author.orcid_id }}</span>
            </p>
            <p>
              <em>Created At:</em> {{ formatDate(author.created_at) }}<br />
              <em>Updated At:</em> {{ formatDate(author.updated_at) }}
            </p>
          </li>
        </ul>
        <p v-else>No authors found.</p>
        <p><strong>Created At:</strong> {{ formatDate(publication.created_at) }}</p>
        <p><strong>Updated At:</strong> {{ formatDate(publication.updated_at) }}</p>
        <UButton label="Back to Publications" @click="goBack" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { ref, watch } from "vue";
import { useRuntimeConfig } from "nuxt/app";
import { formatDate } from "~/utils/formatDate";
import HexGrid from "~/components/HexGrid.vue";
import {usePublicationsStore} from "~/stores/publications";
const publicationStore = usePublicationsStore();

const config = useRuntimeConfig();

// Router
const route = useRoute();
const router = useRouter();

// Loading and error state
const loading = ref(true);
const error = ref<string | null>(null);

// Current publication ID
const publicationId = ref<number>(Number(route.params.id));

// Fetch the publication when the component is mounted or the route changes
const fetchPublicationDetails = async () => {
  loading.value = true;
  error.value = null;

  try {
    await publicationStore.fetchPublication(publicationId.value);
  } catch (err: any) {
    error.value = err.message || "Failed to fetch publication details.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchPublicationDetails);

watch(
  () => route.params.id,
  async (newId) => {
    publicationId.value = Number(newId);
    await fetchPublicationDetails();
  }
);

// Access the fetched publication from the store
const publication = computed(() => publicationStore.selectedPublication);


// Format author name
const formatAuthorName = (author: AuthorSchemaFull): string => {
  const { name, lastname, surname } = author;
  return [name, lastname, surname].filter(Boolean).join(" ") || "Unknown Author";
};

// Go back to the publications list
const goBack = () => {
  router.push("/publications");
};
</script>

<style scoped>
.publication-details-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 1rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: start;
}

main {
  margin-top: 1.5rem;
  flex-grow: 1;
  overflow-y: auto;
}

.error {
  color: red;
}

.loading {
  text-align: center;
}

h2 {
  margin-top: 1rem;
}
</style>
