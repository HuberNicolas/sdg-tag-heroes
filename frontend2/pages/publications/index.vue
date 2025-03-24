<template>
  <div class="publications-container">
    <h1>Publications</h1>

    <!-- Error message -->
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">Loading publications...</div>

    <!-- Publications list -->
    <div v-if="publications && publications.length">
      <ul>

        <li v-for="publication in publications" :key="publication.publication_id">
          <NuxtLink :to="{ name: 'publications-id', params: { id: publication.publication_id } }">
            <div>
              <h3>{{ publication.title || "Untitled Publication" }}</h3>
              <p v-if="publication.authors">
                <strong>Authors:</strong> {{ getAuthors(publication.authors) }}
              </p>
              <p><strong>Created At:</strong> {{ new Date(publication.created_at).toLocaleDateString() }}</p>
            </div>
          </NuxtLink>
        </li>

      </ul>
    </div>

    <!-- No publications found -->
    <div v-else-if="!loading && !publications.length">
      <p>No publications found.</p>
    </div>

    <!-- Pagination: Load More Button -->
    <div v-if="hasMorePages && !loading">
      <UButton @click="loadMore">Load More</UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRuntimeConfig } from "nuxt/app";

// Config and state variables
const config = useRuntimeConfig();
const publications = ref([]);
const currentPage = ref(1);
const totalPages = ref(0);
const hasMorePages = ref(false);
const error = ref<string | null>(null);
const loading = ref(false);

// Fetch publications function
const fetchPublications = async (page = 1) => {
  try {
    loading.value = true;
    error.value = null;

    const response = await $fetch(`${config.public.apiUrl}publications`, {
      params: { page },
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });

    if (page === 1) {
      publications.value = response.items; // Replace publications for new data
    } else {
      publications.value = [...publications.value, ...response.items]; // Append new results
    }

    currentPage.value = response.page;
    totalPages.value = response.pages;
    hasMorePages.value = currentPage.value < totalPages.value;
  } catch (err: any) {
    error.value = err.message || "Failed to fetch publications";
  } finally {
    loading.value = false;
  }
};

// Initial fetch
fetchPublications();

// Load more publications
const loadMore = () => {
  if (hasMorePages.value) {
    fetchPublications(currentPage.value + 1);
  }
};

// Utility function to format authors
const getAuthors = (authors) => {
  return authors.map((author) => author.name || author.full_name).join(", ");
};
</script>

<style scoped>
.publications-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.loading {
  font-size: 1.5rem;
  color: #777;
}

.error {
  color: red;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
}

button {
  display: block;
  margin: 1rem auto;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: white;
}

button:hover {
  background-color: #0056b3;
}
</style>
