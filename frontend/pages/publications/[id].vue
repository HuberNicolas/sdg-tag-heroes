<template>
  <div class="publication-container">
    <h1>Publication</h1>

    <div class="options">
      <label>
        <input type="checkbox" v-model="selectedIncludes" value="authors" />
        Include Authors
      </label>
      <label>
        <input type="checkbox" v-model="selectedIncludes" value="sdg_predictions" />
        Include SDG Predictions
      </label>
    </div>

    <!-- Loading indicator with spinner -->
    <div v-if="loading" class="loading">
      <span class="spinner"></span> Loading publication...
    </div>

    <!-- Error message -->
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Publication Details -->
    <div v-if="publication">
      <h3>{{ publication.title || 'Untitled Publication' }}</h3>
      <p><strong>ID:</strong> {{ publication.publication_id }}</p>
      <p><strong>OAI Identifier:</strong> {{ publication.oai_identifier }}</p>
      <p><strong>Description:</strong> {{ publication.description || 'No description available.' }}</p>
      <p><strong>Publisher:</strong> {{ publication.publisher || 'Unknown' }}</p>
      <p><strong>Date:</strong> {{ publication.date || 'N/A' }}</p>
      <p><strong>Year:</strong> {{ publication.year || 'N/A' }}</p>
      <p><strong>Source:</strong> {{ publication.source || 'N/A' }}</p>
      <p><strong>Language:</strong> {{ publication.language || 'N/A' }}</p>
      <p><strong>Format:</strong> {{ publication.format || 'N/A' }}</p>

      <!-- Authors Section -->
      <div v-if="publication.authors && publication.authors.length">
        <h4>Authors</h4>
        <ul>
          <li v-for="author in publication.authors" :key="author.author_id">
            {{ author.name }} {{ author.lastname }} {{ author.surname }} - ORCID: {{ author.orcid_id || 'N/A' }}
          </li>
        </ul>
      </div>

      <!-- SDG Predictions Section -->
      <div v-if="publication.sdg_predictions">
        <h4>SDG Predictions</h4>
        <p>Predicted: {{ publication.sdg_predictions.predicted ? 'Yes' : 'No' }}</p>
        <p>Last Predicted Goal: {{ publication.sdg_predictions.last_predicted_goal }}</p>
      </div>

      <!-- Faculty, Institute, Division, and DimRed Sections -->
      <div v-if="publication.faculty">
        <h4>Faculty</h4>
        <p>{{ publication.faculty.name || 'Faculty data unavailable' }}</p>
      </div>
      <div v-if="publication.institute">
        <h4>Institute</h4>
        <p>{{ publication.institute.name || 'Institute data unavailable' }}</p>
      </div>
      <div v-if="publication.division">
        <h4>Division</h4>
        <p>{{ publication.division.name || 'Division data unavailable' }}</p>
      </div>
      <div v-if="publication.dim_red">
        <h4>Dimensional Reduction</h4>
        <p>{{ publication.dim_red.description || 'Dimensional reduction data unavailable' }}</p>
      </div>
    </div>
    <div v-else-if="!loading && !publication">
      <p>No publication found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watchEffect } from 'vue';
import { useRoute } from 'vue-router';
import PublicationService from '@/composables/usePublication';
import { PublicationSchema } from '@/types/schemas';
import { debounce } from 'lodash-es';

const publication = ref<PublicationSchema | null>(null);
const loading = ref<boolean>(false);
const error = ref<string | null>(null);

// List of selected includes (checkbox selections)
const selectedIncludes = ref<string[]>([]);
const route = useRoute();

// Fetch a single publication by ID, using selected includes
const fetchPublication = async (id: number | string) => {
  loading.value = true;
  error.value = null;
  publication.value = null;

  try {
    const publicationService = new PublicationService();
    publication.value = await publicationService.getPublicationById([...selectedIncludes.value], Number(id));
  } catch (err: any) {
    error.value = err.message || 'Failed to fetch publication';
  } finally {
    loading.value = false;
  }
};

// Debounce fetch function to avoid excessive API calls
const debouncedFetch = debounce(() => {
  fetchPublication(route.params.id);
}, 300);

// Watch for changes in selectedIncludes and route ID to refmetch data automatically
watchEffect(() => {
  debouncedFetch();
});

// Fetch the publication on initial load
onMounted(() => {
  fetchPublication(route.params.id);
});
</script>

<style scoped>
.publication-container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}

.options {
  margin-bottom: 10px;
}

.error {
  color: red;
}

.loading {
  color: blue;
  display: flex;
  align-items: center;
}

.spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  margin-right: 5px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}
</style>
