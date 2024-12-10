<template>
  <div>
    <div>
      <MinimapContainer></MinimapContainer>
      <BoxplotContainer></BoxplotContainer>
    </div>
    <div class="grid grid-cols-3 gap-4">
      <div>01</div>
      <div>01</div>
      <div>01</div>

      <div>01</div>
      <div>01</div>
      <div>01</div>

      <div>01</div>
      <div>01</div>
      <div>09</div>
    </div>
    <div>
      <p>{{ sdgId }} - {{ levelId }}</p>
      <UButton label="Back to Worlds Overview" @click="goBackToWorlds" />
      <UButton label="Back to World" @click="goBackToWorld" />

      <div class="mt-4">
        <!-- Input for User Interests -->
        <p class="font-bold mb-2">Share your interests:</p>
        <UTextarea
          color="primary"
          variant="outline"
          placeholder="Type your interests here..."
          v-model="userInterests"
        />
        <UButton label="Generate Query" @click="generateInterestsQuery" class="mt-2" />

        <!-- Spinner for Similarity Results -->
        <div v-if="fetchingPublications" class="spinner mt-4">
          Loading similar publications...
        </div>

        <!-- Display Similar Publications -->
        <div v-else class="mt-4">
          <p class="font-bold">Similar Publications:</p>
          <ul v-if="similarPublications.length > 0" class="publication-list">
            <li v-for="publication in similarPublications" :key="publication.publication_id" class="mb-4 border-b pb-2">
              <h3 class="font-semibold">{{ publication.title }}</h3>
              <p><strong>Description:</strong> {{ publication.description }}</p>
              <p><strong>Authors:</strong> {{ formatAuthors(publication.authors) }}</p>
              <p><strong>Score:</strong> {{ publication.score }}</p>
            </li>
          </ul>
          <p v-else>No similar publications found.</p>
        </div>
      </div>

      <p v-if="fetchingQuery">Generating query...</p>
      <p v-else-if="generatedQuery">{{ generatedQuery }}</p>


      <p v-if="fetchingReductions || fetchingPublications">Loading data...</p>
      <p v-else-if="errorReductions || errorPublications">
        Error: {{ errorReductions?.message || errorPublications?.message }}
      </p>
      <p v-else>
        Data loaded successfully
        <PublicationTable :sdgId="sdgId" :levelId="levelId" />
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import {usePredictionsStore} from "~/stores/sdg_predictions";
import { computed, ref, onMounted } from "vue";
import { useRuntimeConfig } from "nuxt/app";
const apiUrl = useRuntimeConfig().public.apiUrl;

// Define page metadata
definePageMeta({
  middleware: ['level-guard'],
});

// Route and router setup
const route = useRoute();
const router = useRouter();

const sdgId = parseInt(route.params.id as string, 10);
const levelId = parseInt(route.params.level_id as string, 10);


// Navigation
const goBackToWorlds = () => {
  router.push("/worlds");
};

const goBackToWorld = () => {
  router.push({ name: 'worlds-id', params: { id: sdgId } });
};

// Use the Pinia stores
const dimensionalityReductionsStore = useDimensionalityReductionsStore();
const publicationsStore = usePublicationsStore();
const predictionsStore = usePredictionsStore();
const sdgStore = useSDGStore();

dimensionalityReductionsStore.setCurrentLevel(levelId);
sdgStore.setSelectedGoal(sdgId);

// State for reductions
const fetchingReductions = ref(false);
const errorReductions = ref<Error | null>(null);
const reductionsData = ref(null);

// State for fetching similar publications
const fetchingPublications = ref(false);
const similarPublications = ref([]);
const errorPublications = ref<Error | null>(null);

// State for predictions
const fetchingPredictions = ref(false);
const errorPredictions = ref<Error | null>(null);
const predictions = ref(null);

// State for SDG goals
const fetchingSDGGoals = ref(false);
const errorSDGGoals = ref<Error | null>(null);

// Load SDG goals if not already loaded
const loadSDGGoals = async () => {
  if (!sdgStore.goals || sdgStore.goals.length === 0) {
    fetchingSDGGoals.value = true;
    errorSDGGoals.value = null;

    try {
      console.log("Fetching SDG goals...");
      await sdgStore.fetchSDGGoals();
      console.log("SDG goals loaded successfully:", sdgStore.goals);
    } catch (err) {
      errorSDGGoals.value = err as Error;
      console.error("Error fetching SDG goals:", err);
    } finally {
      fetchingSDGGoals.value = false;
    }
  } else {
    console.log("SDG goals are already loaded.");
  }
};

// State for user interests
const userInterests = ref("");
const generatedQuery = ref("");
const fetchingQuery = ref(false);
const errorQuery = ref<Error | null>(null);


// Function to generate query based on user interests
const generateInterestsQuery = async () => {
  if (!userInterests.value) {
    alert("Please enter your interests.");
    return;
  }

  fetchingQuery.value = true;
  errorQuery.value = null;

  try {
    // Call the /interests endpoint
    const response = await $fetch(`${apiUrl}profiles/interests`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
      body: {
        interests: userInterests.value,
      },
    });
    generatedQuery.value = response.generated_query;

    // Use the generated query to fetch similar publications
    fetchSimilarPublications(response.generated_query);
  } catch (err) {
    errorQuery.value = err as Error;
    console.error("Error generating interests query:", err);
  } finally {
    fetchingQuery.value = false;
  }
};

// Function to fetch similar publications using the generated query
const fetchSimilarPublications = async (query: string) => {
  fetchingPublications.value = true;
  errorPublications.value = null;

  try {
    const publicationIds = dimensionalityReductionsStore.selectedPoints.length
      ? dimensionalityReductionsStore.selectedPoints.map(point => point.publication_id)
      : []; // Use empty list if no points are selected
    const response = await $fetch(`${apiUrl}publications/similar/5`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
      body: {
        user_query: query,
        publication_ids: publicationIds, // Use hardcoded IDs for now
      },
    });
    similarPublications.value = response.results;
  } catch (err) {
    errorPublications.value = err as Error;
    console.error("Error fetching similar publications:", err);
  } finally {
    fetchingPublications.value = false;
  }
};

// Format authors for display
const formatAuthors = (authors) => {
  return authors.map(author => author.name).join(", ");
};

// Fetch reductions and trigger publications loading only after reductions are ready
const loadReductions = async () => {
  fetchingReductions.value = true;
  errorReductions.value = null;


  try {
    console.log("Fetching reductions...");
    const existingReductions = dimensionalityReductionsStore.reductions[sdgId]?.reductions[levelId];
    if (!existingReductions) {
      await dimensionalityReductionsStore.fetchReductionsPerLevel(sdgId, levelId);
    }
    reductionsData.value = dimensionalityReductionsStore.getReductionsForLevel(sdgId, levelId);

  } catch (err) {
    errorReductions.value = err as Error;
    console.error("Error fetching reductions:", err);
  } finally {
    fetchingReductions.value = false;
  }
};

// Fetch publications based on reductions
const loadPublications = async () => {
  if (!reductionsData.value) {
    console.warn("Reductions data is not initialized. Skipping publications fetch.");
    return; // Ensure reductions are available
  }

  fetchingPublications.value = true;
  errorPublications.value = null;

  try {
    const publicationIds = Array.isArray(reductionsData.value)
      ? reductionsData.value
        .filter((reduction) => reduction && reduction.publication_id)
        .map((reduction) => reduction.publication_id)
      : Object.values(reductionsData.value || {})
        .flat()
        .filter((reduction) => reduction && reduction.publication_id)
        .map((reduction) => reduction.publication_id);

    if (publicationIds.length > 0) {
      await publicationsStore.fetchPublicationsBatch(sdgId, levelId, publicationIds);

      // Todo: outsource
      await predictionsStore.fetchPredictionsBatch(sdgId, levelId, publicationIds);

    } else {
      console.warn("No publication IDs found in reductions data.");
    }
  } catch (err) {
    errorPublications.value = err as Error;
    console.error("Error fetching publications:", err);
  } finally {
    fetchingPublications.value = false;
  }
};

  // Initial load
  const initializeData = async () => {
    try {
      await loadSDGGoals(); // Load SDG goals first
      await loadReductions(); // Load reductions first
      if (reductionsData.value) {
        await loadPublications(); // Load publications only if reductionsData is initialized
      } else {
        console.warn("Reductions data is not ready after loadReductions.");
      }
    } catch (err) {
      console.error("Error initializing data:", err);
    }
  };

  // Call initializeData when the component is mounted
  onMounted(() => {
    initializeData();
  });
</script>
