<template>
  <div v-if="selectedPublication" class="mx-auto p-6 bg-white shadow-lg rounded-lg max-h-[80vh] overflow-y-auto">
    <!-- Title -->
    <h2 class="text-xl font-bold text-gray-800 mb-4">
      {{ selectedPublication.title || "Untitled Publication" }}
    </h2>

    <!-- Authors & Year -->
    <p class="text-gray-600">
      <span v-if="selectedPublication.authors && selectedPublication.authors.length > 0">
        <strong>Authors:</strong> {{ selectedPublication.authors.map(a => a.name).join(", ") }}
      </span>
      <span v-if="selectedPublication.year" class="ml-4">
        <strong>Year:</strong> {{ selectedPublication.year }}
      </span>
    </p>

    <!-- Keywords -->
    <div v-if="keywords && keywords.keywords.length > 0" class="mt-4">
      <strong class="text-gray-700">Keywords:</strong>
      <span v-for="(keyword, index) in keywords.keywords" :key="index" class="bg-gray-200 text-gray-700 px-2 py-1 rounded-lg text-sm mr-2">
        {{ keyword }}
      </span>
    </div>

    <!-- Summary -->
    <div v-if="summary && summary.summary" class="mt-4">
      <h3 class="text-lg font-semibold text-gray-700">Summary</h3>
      <p class="text-gray-700">{{ summary.summary }}</p>
    </div>

    <!-- Fact -->
    <div v-if="fact && fact.content" class="mt-4 bg-blue-100 p-3 rounded-lg">
      <h3 class="text-lg font-semibold text-blue-700">Did You Know?</h3>
      <p class="text-blue-700">{{ fact.content }}</p>
    </div>

    <!-- SDG Predictions -->
    <div v-if="selectedPublication.sdgPredictions && selectedPublication.sdgPredictions.length > 0" class="mt-4">
      <h3 class="text-lg font-semibold text-green-700">SDG Predictions</h3>
      <ul class="list-disc list-inside text-gray-700">
        <li v-for="(sdg, index) in selectedPublication.sdgPredictions" :key="index">
          SDG {{ sdg.sdgId }}: {{ sdg.reasoning }}
        </li>
      </ul>
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

    // Function to fetch additional details when publication changes
    const fetchPublicationDetails = async () => {
      if (selectedPublication.value) {
        const publicationId = selectedPublication.value.publicationId;
        try {
          keywords.value = await getPublicationKeywords(publicationId);
          fact.value = await getPublicationFact(publicationId);
          summary.value = await getPublicationSummary(publicationId);
        } catch (error) {
          console.error("Error fetching additional publication details:", error);
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
      summary
    };
  }
};
</script>
