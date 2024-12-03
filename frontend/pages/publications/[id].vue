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
          <p class="text-sm mt-4">---</p>
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

const config = useRuntimeConfig();

// Router
const route = useRoute();
const router = useRouter();

// Current publication ID
const publicationId = ref<number>(Number(route.params.id));

// Fetch publication details using useAsyncData
const { data: publication, pending: loading, error, refresh } = useAsyncData(
  `publication-${publicationId.value}`, // Unique key for the fetch
  () =>
    $fetch<PublicationSchemaFull>(`${config.public.apiUrl}publications/${publicationId.value}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    }),
  { immediate: true } // Fetch data on component mount
);

// Watch for route changes to refresh data
watch(
  () => route.params.id,
  (newId) => {
    publicationId.value = Number(newId);
    refresh(); // Refresh the fetch with new ID
  }
);

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
