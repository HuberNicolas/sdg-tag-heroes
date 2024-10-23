<template>
  <div class="publications-container">
    <h1>Publications</h1>
    <form @submit.prevent="onSubmitForm">
      <label>
        <input type="checkbox" v-model="selectedIncludes" value="authors" />
        Include Authors
      </label>
      <label>
        <input type="checkbox" v-model="selectedIncludes" value="sdg_predictions" />
        Include SDG Predictions
      </label>
      <button type="submit">Fetch Publications</button>
    </form>
    <!-- Error message -->
    <div v-if="error" class="error">{{ error }}</div>
    <!-- Loading state -->
    <div v-if="loading" class="loading">Loading publications...</div>

    <div v-if="publications && publications.length">
      <ul>
        <li v-for="publication in publications" :key="publication.id">
          <h3>{{ publication.title }}</h3>
          <p v-if="publication.authors"><strong>Authors:</strong> {{ getAuthors(publication.authors) }}</p>
          <div v-if="publication.sdg_predictions" class="sdg-predictions">
            <h4>SDG Predictions</h4>
            <ul>
              <li v-for="(value, key) in sdgPredictionKeys(publication.sdg_predictions)" :key="key">
                <strong>{{ key }}:</strong> {{ value }}
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </div>
    <div v-else-if="!loading && !publications.length">
      <p>No publications found.</p>
    </div>
  </div>

  <!-- Pagination: Load More Button -->
    <div v-if="hasMorePages && !loading">
      <button @click="loadMore">Load More</button>
    </div>

    <div v-else-if="!loading && !publications.length">
      <p>No publications found.</p>
    </div>

</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import PublicationService from '@/services/PublicationService';

const publications = ref<any[]>([]);
const loading = ref<boolean>(false);
const error = ref<string | null>(null);

// Pagination State
const currentPage = ref<number>(1);
const totalPages = ref<number>(0);
const hasMorePages = ref<boolean>(false);

// List of selected includes (checkbox selections)
const selectedIncludes = ref<string[]>([]);

// Change how fetchPublications is called
const fetchPublications = async (page = 1) => {
  loading.value = true;
  error.value = null;

  try {
    const publicationService = new PublicationService();
    const response = await publicationService.getPublications([...selectedIncludes.value], page);

    if (page === 1) {
      publications.value = response.items; // Reset publications on form submit
    } else {
      publications.value = [...publications.value, ...response.items]; // Append results on "Load More"
    }

    currentPage.value = response.page;
    totalPages.value = response.pages;
    hasMorePages.value = currentPage.value < totalPages.value;
  } catch (err: any) {
    error.value = err.message || 'Failed to fetch publications';
  } finally {
    loading.value = false;
  }
};


onMounted(() => {
  fetchPublications();
});

const loadMore = () => {
  if (currentPage.value < totalPages.value) {
    fetchPublications(currentPage.value + 1);
  }
};

const onSubmitForm = () => {
  currentPage.value = 1; // Reset to the first page
  fetchPublications();   // Fetch the publications with the selected filters
};

// Helper function to format authors
const getAuthors = (authors: any[] | null) => {
  return authors ? authors.map(author => author.name).join(', ') : 'Unknown';
};

// Helper function to filter SDG prediction keys and exclude metadata
const sdgPredictionKeys = (sdg_predictions: any) => {
  // Exclude metadata fields like 'publication_id', 'predicted', 'created_at', and 'updated_at'
  const excludeKeys = ['publication_id', 'predicted', 'last_predicted_goal', 'created_at', 'updated_at'];
  return Object.fromEntries(Object.entries(sdg_predictions).filter(([key]) => !excludeKeys.includes(key)));
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
</style>
