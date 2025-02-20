<template>
  <div>
    <!-- Button to open modal -->
    <button class="btn" @click="openModal">Continue Labeling</button>

    <!-- Modal Dialog -->
    <dialog id="model_labeling" class="modal">
      <div class="modal-box max-w-3xl">
        <!-- Close Button -->
        <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"  @click="closeModal">✕</button>

        <!-- Tabs -->
        <div class="tabs">
          <button
            class="tab tab-bordered"
            :class="{ 'tab-active': activeTab === 'similar' }"
            @click="activeTab = 'similar'"
          >
            Similar Publications
          </button>
          <button
            class="tab tab-bordered"
            :class="{ 'tab-active': activeTab === 'scenarios' }"
            @click="activeTab = 'scenarios'"
          >
            Scenarios
          </button>
        </div>

        <!-- Loading Indicator -->
        <div v-if="loading" class="text-center">
          <span class="loading loading-bars loading-lg"></span>
          <p>Fetching publication details...</p>
        </div>

        <!-- Display Similar Publications Once Loaded -->
        <div v-if="activeTab === 'similar'" class="relative mx-auto p-4 bg-white shadow-lg rounded-lg max-h-[80vh] overflow-y-auto">
          <!-- Similar Publications Content -->
          <h2 class="text-xl font-bold text-gray-800 mb-4">Select a Similar Publication</h2>
          <div class="max-h-64 overflow-y-auto space-y-4">
            <div
              v-for="pub in similarPublications"
              :key="pub.publicationId"
              class="p-4 border rounded-lg cursor-pointer hover:bg-gray-100 transition"
              @click="selectPublication(pub)"
            >
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-semibold">{{ pub.title || "Untitled Publication" }}</h3>
                <span class="text-gray-600">Similarity: {{ (pub.score * 100).toFixed(2) }}%</span>
                <UButton size="sm" color="primary" variant="solid">
                  <NuxtLink :to="`/labeling/${pub.publicationId}`">Continue Labeling</NuxtLink>
                </UButton>
              </div>

              <!-- Keywords -->
              <div class="mt-2">
                <div v-if="keywordsLoading[pub.publicationId]" class="text-center">
                  <span class="loading loading-bars loading-sm"></span> Loading Keywords...
                </div>
                <div v-else-if="keywords[pub.publicationId]?.keywords?.length">
                  <strong class="text-gray-700">Keywords:</strong>
                  <span
                    v-for="(keyword, index) in keywords[pub.publicationId].keywords"
                    :key="index"
                    class="bg-gray-200 text-gray-700 px-2 py-1 rounded-lg text-sm mr-2"
                  >
                    {{ keyword }}
                  </span>
                </div>
              </div>

              <!-- Fact -->
              <div class="mt-2">
                <div v-if="factLoading[pub.publicationId]" class="text-center">
                  <span class="loading loading-bars loading-sm"></span> Loading Fact...
                </div>
                <div v-else-if="fact[pub.publicationId]?.content" class="mt-2 bg-blue-100 p-2 rounded-lg">
                  <h3 class="text-sm font-semibold text-blue-700">Did You Know?</h3>
                  <p class="text-blue-700 text-sm">{{ fact[pub.publicationId].content }}</p>
                </div>
              </div>

              <!-- Summary -->
              <div class="mt-2">
                <div v-if="summaryLoading[pub.publicationId]" class="text-center">
                  <span class="loading loading-bars loading-sm"></span> Loading Summary...
                </div>
                <div v-else-if="summary[pub.publicationId]?.summary" class="mt-2">
                  <h3 class="text-sm font-semibold text-gray-700">Summary</h3>
                  <p class="text-gray-700 text-sm">{{ summary[pub.publicationId].summary }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- No Similar Publications Found -->
          <div v-if="similarPublications.length === 0" class="text-center text-gray-500 mt-6">
            <p>No similar publications found.</p>
          </div>

          <!-- Continue to Labeling Button -->
          <div class="mt-6 text-right">
            <UButton v-if="selectedPublication" size="sm" color="primary" variant="solid">
              <NuxtLink :to="`/labeling/${selectedPublication.publicationId}`">Continue Labeling</NuxtLink>
            </UButton>
          </div>
        </div>

        <!-- Display Publications by Scenario Once Loaded -->
        <div v-if="activeTab === 'scenarios'" class="relative mx-auto p-4 bg-white shadow-lg rounded-lg max-h-[80vh] overflow-y-auto">
          <!-- Scenarios Content -->
          <h2 class="text-xl font-bold text-gray-800 mb-4">Select a Scenario</h2>
          <div class="flex gap-2 mb-4">
            <button
              v-for="scenario in scenarioButtons"
              :key="scenario.name"
              class="btn btn-outline"
              @click="fetchPublicationsByScenario(scenario.type)"
            >
              <UIcon :name="scenario.icon" class="w-4 h-4 mr-2" />
              {{ scenario.name }}
            </button>
          </div>

          <div class="max-h-64 overflow-y-auto space-y-4">
            <div
              v-for="pub in scenarioPublications"
              :key="pub.publicationId"
              class="p-4 border rounded-lg cursor-pointer hover:bg-gray-100 transition"
              @click="selectPublication(pub)"
            >
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-semibold">{{ pub.title || "Untitled Publication" }}</h3>
                <UButton size="sm" color="primary" variant="solid">
                  <NuxtLink :to="`/labeling/${pub.publicationId}`">Continue Labeling</NuxtLink>
                </UButton>
              </div>

              <!-- Keywords -->
              <div class="mt-2">
                <div v-if="keywordsLoading[pub.publicationId]" class="text-center">
                  <span class="loading loading-bars loading-sm"></span> Loading Keywords...
                </div>
                <div v-else-if="keywords[pub.publicationId]?.keywords?.length">
                  <strong class="text-gray-700">Keywords:</strong>
                  <span
                    v-for="(keyword, index) in keywords[pub.publicationId].keywords"
                    :key="index"
                    class="bg-gray-200 text-gray-700 px-2 py-1 rounded-lg text-sm mr-2"
                  >
                    {{ keyword }}
                  </span>
                </div>
              </div>

              <!-- Fact -->
              <div class="mt-2">
                <div v-if="factLoading[pub.publicationId]" class="text-center">
                  <span class="loading loading-bars loading-sm"></span> Loading Fact...
                </div>
                <div v-else-if="fact[pub.publicationId]?.content" class="mt-2 bg-blue-100 p-2 rounded-lg">
                  <h3 class="text-sm font-semibold text-blue-700">Did You Know?</h3>
                  <p class="text-blue-700 text-sm">{{ fact[pub.publicationId].content }}</p>
                </div>
              </div>

              <!-- Summary -->
              <div class="mt-2">
                <div v-if="summaryLoading[pub.publicationId]" class="text-center">
                  <span class="loading loading-bars loading-sm"></span> Loading Summary...
                </div>
                <div v-else-if="summary[pub.publicationId]?.summary" class="mt-2">
                  <h3 class="text-sm font-semibold text-gray-700">Summary</h3>
                  <p class="text-gray-700 text-sm">{{ summary[pub.publicationId].summary }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- No Publications Found for Scenario -->
          <div v-if="scenarioPublications.length === 0" class="text-center text-gray-500 mt-6">
            <p>No publications found for this scenario.</p>
          </div>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import usePublications from "~/composables/usePublications";
import { ScenarioType } from "~/types/enums";

const route = useRoute();
const { getPublicationById, getSimilarPublications, getPublicationKeywords, getPublicationFact, getPublicationSummary, getPublicationsByScenario } = usePublications();

const publication = ref(null);
const similarPublications = ref([]);
const scenarioPublications = ref([]);
const selectedPublication = ref(null);

const loading = ref(false);
const keywords = ref<Record<number, any>>({});
const fact = ref<Record<number, any>>({});
const summary = ref<Record<number, any>>({});
const keywordsLoading = ref<Record<number, boolean>>({});
const factLoading = ref<Record<number, boolean>>({});
const summaryLoading = ref<Record<number, boolean>>({});

const activeTab = ref<'similar' | 'scenarios'>('similar');

const scenarioButtons = [
  { icon: "i-heroicons-check-badge", name: "Confirm", type: ScenarioType.CONFIRM },
  { icon: "i-heroicons-map", name: "Explore", type: ScenarioType.EXPLORE },
  { icon: "i-heroicons-magnifying-glass", name: "Investigate", type: ScenarioType.INVESTIGATE },
  { icon: "i-heroicons-scale", name: "Tiebreaker", type: ScenarioType.TIEBREAKER },
];

// Function to open modal and start loading
const openModal = async () => {
  document.getElementById("model_labeling").showModal();
  if (activeTab.value === 'similar') {
    await fetchPublicationAndSimilarResults();
  }
};

// Function to close modal
const closeModal = () => {
  document.getElementById("model_labeling").close();
};

// Function to switch tabs without closing the modal
const setActiveTab = (tab: 'similar' | 'scenarios') => {
  activeTab.value = tab;
  if (tab === 'scenarios') {
    fetchPublicationsByScenario(ScenarioType.EXPLORE);
  }
};

// Function to fetch the publication and find similar ones
const fetchPublicationAndSimilarResults = async () => {
  const publicationId = Number(route.params.publicationId);
  if (!publicationId) return;

  loading.value = true;
  try {
    // Fetch the publication by ID
    publication.value = await getPublicationById(publicationId);

    if (publication.value) {
      const userQuery = publication.value.title || publication.value.description || "";

      // Fetch top 4 similar publications (so we can skip the first one)
      const response = await getSimilarPublications(4, userQuery);
      let results = response?.results || [];

      // Skip the first result (assuming it's the same publication)
      if (results.length > 1) {
        results = results.slice(1);
      }

      similarPublications.value = results;

      // Fetch additional details for each similar publication
      results.forEach((pub) => fetchAdditionalDetails(pub.publicationId));
    }
  } catch (error) {
    console.error("Error fetching publication and similar results:", error);
  } finally {
    loading.value = false;
  }
};

// Function to fetch publications by scenario type
const fetchPublicationsByScenario = async (scenarioType: ScenarioType) => {
  loading.value = true;
  try {
    const publications = await getPublicationsByScenario(scenarioType, 4);
    scenarioPublications.value = publications;

    // Fetch additional details for each publication
    publications.forEach((pub) => fetchAdditionalDetails(pub.publicationId));
  } catch (error) {
    console.error("Error fetching publications by scenario:", error);
  } finally {
    loading.value = false;
  }
};

// Function to fetch keywords, fact, and summary for a given publication
const fetchAdditionalDetails = async (publicationId: number) => {
  keywordsLoading.value[publicationId] = true;
  factLoading.value[publicationId] = true;
  summaryLoading.value[publicationId] = true;

  try {
    const [kw, fc, sm] = await Promise.all([
      getPublicationKeywords(publicationId),
      getPublicationFact(publicationId),
      getPublicationSummary(publicationId)
    ]);

    keywords.value[publicationId] = kw;
    fact.value[publicationId] = fc;
    summary.value[publicationId] = sm;
  } catch (error) {
    console.error("Error fetching additional details:", error);
  } finally {
    keywordsLoading.value[publicationId] = false;
    factLoading.value[publicationId] = false;
    summaryLoading.value[publicationId] = false;
  }
};

// Function to select a publication from the list
const selectPublication = (pub) => {
  selectedPublication.value = pub;
};
</script>
