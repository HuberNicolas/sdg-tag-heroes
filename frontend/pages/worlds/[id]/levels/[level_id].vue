<template>
  <div>
    <div class="grid grid-cols-6 gap-4">
      <div class="col-span-3"><MinimapContainer></MinimapContainer></div>
      <div class="col-span-3"><!-- Input for User Interests -->
        <p class="font-bold mb-2">Share your interests:</p>
        <UTextarea
          color="primary"
          variant="outline"
          placeholder="Type your interests here..."
          v-model="userInterests"
        />
        <UButton
          label="Generate Query"
          @click="generateInterestsQuery"
          class="mt-2"
        />
        <p v-if="fetchingQuery" class="text-gray-500 italic">Generating query...</p>
        <div class="mt-2">
          <UTextarea
            resize
            :placeholder="fetchingQuery ? 'Generating Query...' : (generatedQuery || 'Search...')"
            :value="generatedQuery"
          />
        </div>


        <div>
          <!-- Spinner for Loading -->
          <div v-if="fetchingPublications" class="spinner mt-4">
            Loading recommended publications...
          </div>

          <!-- Publications Table -->
          <div v-else class="mt-4">
            <p class="font-bold mb-2">Recommended Publications:</p>
            <div class="overflow-x-auto">
              <table class="min-w-full table-auto border-collapse border border-gray-200">
                <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Title</th>
                  <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Description</th>
                  <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Score</th>
                </tr>
                </thead>
                <tbody>
                <tr
                  v-for="publication in sortedPublications"
                  :key="publication.publication_id"
                  class="hover:bg-gray-50 cursor-pointer"
                  @click="select(publication)"
                >
                  <td class="px-4 py-2 text-sm text-gray-700">
                    <a
                      :href="`/labeling/${publication.publication_id}`"
                      class="text-blue-600 hover:underline"
                      @click.stop
                    >
                      {{ publication.title.length > 30 ? publication.title.slice(0, 30) + '...' : publication.title }}
                    </a>
                  </td>
                  <td class="px-4 py-2 text-sm text-gray-700 relative group">
    <span>
      {{ publication.description.length > 50 ? publication.description.slice(0, 50) + '...' : publication.description }}
    </span>
                    <!-- Tooltip -->
                    <div class="absolute hidden group-hover:block top-full left-0 mt-1 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
                      {{ publication.description }}
                    </div>
                  </td>
                  <td class="px-4 py-2 text-sm text-gray-700">
                    {{ publication.score }}
                  </td>
                </tr>
                </tbody>

              </table>
            </div>
          </div>
        </div>
      </div>


      <div class="col-span-3"><BoxplotContainer></BoxplotContainer></div>
      <div class="col-span-3"><UButton label="Back to Worlds Overview" @click="goBackToWorlds" />
        <UButton label="Back to World" @click="goBackToWorld" /></div>
      <div  class="col-span-6">
        <!-- <p>{{ sdgId }} - {{ levelId }}</p> -->
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

    dimensionalityReductionsStore.fetchUserCoordinates(generatedQuery.value, sdgId, levelId);
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
const sortedPublications = computed(() =>
  similarPublications.value
    .sort((a, b) => b.score - a.score) // Sort by score descending
    .map((pub) => ({
      publication_id: pub.publication_id,
      title: pub.title,
      description: pub.description,
      authors: pub.authors, // Pass raw authors to use with formatAuthors
      score: pub.score,
    }))
);

function select(publication) {
  router.push({ name: 'labeling-id', params: { id: publication.publication_id } });
}


definePageMeta({
  layout: 'user'
})
</script>
