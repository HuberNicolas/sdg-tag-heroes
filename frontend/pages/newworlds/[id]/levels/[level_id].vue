<template>
  <div class="grid grid-cols-3 p-2 gap-2 h-screen">

    <div class="col-1 p-2 h-full">
      <div class="grid grid-cols-2 gap-4 w-full h-1/2">

        <UTooltip
          v-for="(icon, index) in leftIcons"
          :key="index"
          :text="icon.tooltip"
          :popper="{ arrow: true }"
        >
          <UButton
            class="flex flex-col items-center justify-center w-56 h-56 bg-gray-200 rounded-full shadow-md hover:bg-gray-300 focus:outline-none"
            :key="index"
            @click="handleButtonClick(index)"
          >
            <component
              :is="icon.component"
              class="w-36 h-36"
              :fontControlled="false"
            />
            <UChip :text="icon.value" size="3xl" class="mt-2" />
            <p class="text-sm mt-2 text-gray-600">{{ icon.label }}</p>
          </UButton>
        </UTooltip>

        <RaincloudplotContainer></RaincloudplotContainer>

      </div>
    </div>
    <div class="col-2 p-2 h-full">

      <div class="grid grid-rows-7 grid-cols-1 gap-4 h-full">
        <div class="col-span-1 row-span-1">
          <div class="flex items-center gap-4">

            <!-- SDG Icon Container -->
            <div class="flex items-center justify-center w-20 h-20 border-4 rounded-lg bg-gray-100">
              <img
                v-if="sdgIcon"
                :src="`data:image/svg+xml;base64,${sdgIcon}`"
                :alt="`SDG ${sdgId} Icon`"
                class="w-16 h-16 object-contain"
              />
              <span v-else class="text-gray-500">SDG {{ sdgId }}</span>
            </div>

            <!-- Level Indicator with Dynamic Colors -->
            <div
              class="flex-1 px-4 py-2 rounded-lg shadow flex items-center justify-between"
              :class="levelClasses"
            >
              <span class="text-xs font-semibold uppercase">Level</span>
              <span class="text-lg font-bold">{{ levelText }}</span>
            </div>
          </div>

        </div>


        <div class="col-span-1 row-span-5 h-full">
          <!--Table with selected and ranked Publications-->

          <!-- Spinner for Loading -->
          <div v-show="fetchingPublications" class="spinner">
            Loading recommended publications...
          </div>

          <!-- Error State -->
          <div v-show="errorPublications" class="text-red-500">
            Error: {{ errorPublications?.message }}
          </div>

          <!-- Display Publications Table -->
          <div class="h-9" v-show="!fetchingPublications && !errorPublications">
            <p class="font-bold mb-2">Recommended Publications:</p>
            <div class="">
              <table class="min-w-full table-fixed border-collapse border h-full overflow-y-auto border-gray-200">
                <thead class="bg-gray-100 sticky top-0 z-10">
                <tr>
                  <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Title</th>
                  <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Description</th>
                  <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">SDG-Coin Value</th>
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
                      {{ publication.title.length > 30 ? publication.title.slice(0, 30) + "..." : publication.title }}
                    </a>
                  </td>
                  <td class="px-4 py-2 text-sm text-gray-700 relative group">
            <span>
              {{ publication.description.length > 50
              ? publication.description.slice(0, 50) + "..."
              : publication.description
              }}
            </span>
                    <!-- Tooltip -->
                    <div
                      class="absolute hidden group-hover:block top-full left-0 mt-1 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
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

        <div class="col-span-1 row-span-1">
          <UButton label="Back to Worlds Overview" @click="goBackToWorlds" />
          <UButton label="Back to World" @click="goBackToWorld" />
        </div>
      </div>


    </div>
    <div class="col-2 p-2 h-full">

      <div class="grid grid-rows-6 grid-cols-1 gap-4 h-full">
        <div class="col-span-1 row-span-3">
          <!-- Map -->
          <MinimapContainer></MinimapContainer>


        </div>
        <div class="col-span-1 row-span-3">
          <!-- Input for User Interests -->
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
              :placeholder="fetchingQuery ? 'Generating Query...' : (generatedQuery || 'Generated Personalized User Search Query')"
              :value="generatedQuery"
            />
          </div>

          <!-- Spinner for Loading -->
          <div v-if="fetchingPublications" class="spinner mt-4">
            Loading recommended publications...
          </div>


        </div>
      </div>

    </div>
  </div>

</template>

<script setup lang="ts">


import alConfirm from "~/assets/al_confirm.svg?component";
import alExplore from "~/assets/al_explore.svg?component";
import alInvestigate from "~/assets/al_investigate.svg?component";
import alTiebreaker from "~/assets/al_tiebreaker.svg?component";

const leftIcons = [
  { component: alConfirm, action: "confirm", value: "$", label: "Confirm", tooltip: "This is the Confirm option" },
  { component: alExplore, action: "explore", value: "$$", label: "Explore", tooltip: "This is the Explore option" },
  {
    component: alInvestigate,
    action: "investigate",
    value: "$$$",
    label: "Investigate",
    tooltip: "This is the Investigate option"
  },
  {
    component: alTiebreaker,
    action: "tiebreaker",
    value: "$$$$",
    label: "Tiebreaker",
    tooltip: "This is the Tiebreaker option"
  },


];

const handleClick = (action: string) => {
  console.log(`Button clicked: ${action}`);
  // Add action handling logic here, e.g., navigation or API calls
};

definePageMeta({
  middleware: ["level-guard"],
  layout: "user"
});


import { useRoute, useRouter } from "vue-router";
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { usePredictionsStore } from "~/stores/sdg_predictions";
import { computed, ref, onMounted } from "vue";
import { useRuntimeConfig } from "nuxt/app";

const apiUrl = useRuntimeConfig().public.apiUrl;

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
  router.push({ name: "worlds-id", params: { id: sdgId } });
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
        Authorization: `Bearer ${localStorage.getItem("access_token")}`
      },
      body: {
        interests: userInterests.value
      }
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
        Authorization: `Bearer ${localStorage.getItem("access_token")}`
      },
      body: {
        user_query: query,
        publication_ids: publicationIds // Use hardcoded IDs for now
      }
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

const sdgIcon = computed(() => {
  const goal = sdgStore.goals?.items?.find((g) => g.id === sdgId);
  return goal?.icon || null;
});

const levelClasses = computed(() => {
  switch (levelId) {
    case 1:
      return "border-4 border-[#cd7f32] text-[#cd7f32] bg-[#fff8e1]"; // Bronze
    case 2:
      return "border-4 border-[#c0c0c0] text-[#c0c0c0] bg-[#f5f5f5]"; // Silver
    case 3:
      return "border-4 border-[#ffd700] text-[#ffd700] bg-[#fffde7]"; // Gold
    default:
      return "border-4 border-gray-400 text-gray-400 bg-gray-100"; // Default
  }
});

const levelText = computed(() => {
  switch (levelId) {
    case 1:
      return "Bronze";
    case 2:
      return "Silver";
    case 3:
      return "Gold";
    default:
      return `Level ${levelId}`;
  }
});


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

const FILTER_RANGES = [
  { lower_limit: 0.9, upper_limit: 1.0 }, // bronze (default filter range)
  { lower_limit: 0.8, upper_limit: 0.9 }, // silver
  { lower_limit: 0.5, upper_limit: 0.9 }, // gold
];

const fetchPublicationsByMetric = async (metricType, order, topN, noHighPredictions, sdgField = `sdg${sdgId}`) => {
  fetchingPublications.value = true;
  errorPublications.value = null;

  try {
    const filterRange = FILTER_RANGES[levelId - 1] || FILTER_RANGES[0]; // Adapt range to level
    const response = await $fetch(`${apiUrl}sdg_predictions/publications/metrics/filter/${metricType}/${order}/${topN}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        "Content-Type": "application/json",
      },
      body: {
        sdg_field: sdgField,
        lower_limit: filterRange.lower_limit,
        upper_limit: filterRange.upper_limit,
        no_high_predictions: noHighPredictions,
      },
    });

    // Extract publication IDs
    const publicationIds = response.sorted_results.map((result) => result.publication_id);

    // Fetch full publication details
    await publicationsStore.fetchPublicationsBatch(sdgId, levelId, publicationIds);

    // Update scores in the store and synchronize selected publications
    response.sorted_results.forEach((result) => {
      const publication = publicationsStore.publications[sdgId]?.[levelId]?.[result.publication_id];
      if (publication) {
        publication.score = result.entropy*(noHighPredictions+1); // Use entropy as the score
      }
    });

    // Sync selected publications with the fetched results
    publicationsStore.selectedPublications = publicationIds.map(
      (id) => publicationsStore.publications[sdgId]?.[levelId]?.[id]
    ).filter((pub) => pub);

    console.log("Selected publications after fetch:", publicationsStore.selectedPublications);
  } catch (err) {
    errorPublications.value = err as Error;
    console.error("Error fetching publications by metric:", err);
  } finally {
    fetchingPublications.value = false;
  }
};

// Assign buttons with respective logic
const handleButtonClick = (buttonIndex) => {
  const noHighPredictions = buttonIndex; // Button 0 → no_high_predictions = 0, Button 1 → 1, and so on
  fetchPublicationsByMetric("entropy", "top", 10, noHighPredictions);
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

const sortedPublications = computed(() => {
  // Assuming that publications are stored in the store under sdgId and levelId
  //const publications = publicationsStore.getPublications(sdgId, levelId);
  const publications = publicationsStore.getSelectedPublications;

  // Sort publications by score in descending order
  return Object.values(publications)
    .sort((a, b) => b.score - a.score)
    .map((pub) => ({
      publication_id: pub.publication_id,
      title: pub.title,
      description: pub.description,
      authors: pub.authors,
      score: pub.score
    }));
});


// Function to select and fetch publication details
function select(publication) {
  publicationsStore.fetchPublication(publication.publication_id); // Fetch publication details
  router.push({ name: "labeling-id", params: { id: publication.publication_id } });
}


</script>


<style scoped>

</style>
