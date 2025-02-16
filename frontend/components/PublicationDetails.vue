<template>
  <div v-if="selectedPublication" class="relative mx-auto p-6 bg-white shadow-lg rounded-lg max-h-[80vh] overflow-y-auto">

    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-800 mb-4">
        {{ selectedPublication.title || "Untitled Publication" }} ({{selectedPublication.year}})
      </h2>

      <UButton
        icon="mdi-tag-outline"
        size="sm"
        color="primary"
        variant="solid"
        label="Button"
        :trailing="false"
      >
        <NuxtLink :to="`/labeling2/${selectedPublication.publicationId}`">Label</NuxtLink>
      </UButton>
    </div>

    <!-- Authors & Year -->

    <!--
    <p class="text-gray-600">
      <span v-if="selectedPublication.authors && selectedPublication.authors.length > 0">
        <strong>Authors:</strong> {{ selectedPublication.authors.map(a => a.name).join(", ") }}
      </span>
      <span v-if="selectedPublication.year" class="ml-4">
        <strong>Year:</strong> {{ selectedPublication.year }}
      </span>
    </p>
     -->

    <!-- Keywords -->
    <div class="mt-4">
      <div v-if="keywordsLoading" class="text-center">
        <span class="loading loading-bars loading-lg"></span> Loading Keywords...
      </div>
      <div v-else-if="keywords && keywords.keywords.length > 0">
        <strong class="text-gray-700">Keywords:</strong>
        <span v-for="(keyword, index) in keywords.keywords" :key="index" class="bg-gray-200 text-gray-700 px-2 py-1 rounded-lg text-sm mr-2">
          {{ keyword }}
        </span>
      </div>
    </div>

    <!-- Fact -->
    <div class="mt-4">
      <div v-if="factLoading" class="text-center">
        <span class="loading loading-bars loading-lg"></span> Loading Fact...
      </div>
      <div v-else-if="fact && fact.content" class="mt-4 bg-blue-100 p-3 rounded-lg">
        <h3 class="text-lg font-semibold text-blue-700">Did You Know?</h3>
        <p class="text-blue-700">{{ fact.content }}</p>
      </div>
    </div>

    <!-- Summary -->
    <div class="mt-4">
      <div v-if="summaryLoading" class="text-center">
        <span class="loading loading-bars loading-lg"></span> Loading Summary...
      </div>
      <div v-else-if="summary && summary.summary" class="mt-4">
        <h3 class="text-lg font-semibold text-gray-700">Summary</h3>
        <p class="text-gray-700">{{ summary.summary }}</p>
      </div>
    </div>
  </div>

  <div v-else class="text-center text-gray-500 mt-6">No publication selected.</div>
</template>


<script>
import { ref, watch, onMounted } from "vue";
import { usePublicationsStore } from "@/stores/publications";
import usePublications from "@/composables/usePublications";

export default {
  setup() {
    const publicationsStore = usePublicationsStore();
    const { getPublicationKeywords, getPublicationFact, getPublicationSummary } = usePublications();

    const selectedPublication = ref(publicationsStore.selectedPublication);
    const keywords = ref(null);
    const fact = ref(null);
    const summary = ref(null);

    const keywordsLoading = ref(false);
    const factLoading = ref(false);
    const summaryLoading = ref(false);

    // Function to fetch additional details when publication changes
    const fetchPublicationDetails = async () => {
      if (selectedPublication.value) {
        const publicationId = selectedPublication.value.publicationId;

        // Set loading flags
        keywordsLoading.value = true;
        factLoading.value = true;
        summaryLoading.value = true;

        try {
          // Clear previous content while loading new data
          keywords.value = null;
          fact.value = null;
          summary.value = null;

          // Fetch data
          keywords.value = await getPublicationKeywords(publicationId);
          fact.value = await getPublicationFact(publicationId);
          summary.value = await getPublicationSummary(publicationId);

        } catch (error) {
          console.error("Error fetching additional publication details:", error);
        } finally {
          // Set loading flags to false after data is fetched
          keywordsLoading.value = false;
          factLoading.value = false;
          summaryLoading.value = false;
        }
      }
    };

    // Watch for changes in the selected publication and fetch additional data
    watch(() => publicationsStore.selectedPublication, (newPublication) => {
      selectedPublication.value = newPublication;
      fetchPublicationDetails();
    }, { immediate: true });

    // Fetch details on mount if publication is already selected
    onMounted(() => {
      if (selectedPublication.value) {
        fetchPublicationDetails();
      }
    });

    return {
      selectedPublication,
      keywords,
      fact,
      summary,
      keywordsLoading,
      factLoading,
      summaryLoading
    };
  }
};
</script>

