<template>
  <div class="frame-container">
    <div class="frame-title"><b>Decide</b> to label an interesting publication</div>
    <div v-if="selectedPublication" class="relative mx-auto p-5 bg-surface-2/70 border border-line rounded-xl max-h-[80vh] overflow-y-auto">

      <h2 class="text-xl font-bold tracking-tight text-fg mb-4">
        {{ selectedPublication.title || "Untitled Publication" }} ({{selectedPublication.year}})
      </h2>

      <!-- Keywords -->
      <div class="mt-4">
        <div v-if="keywordsLoading" class="text-center">
          <LoadingState size="sm" label="llm is picking keywords" />
        </div>
        <div v-else-if="keywords && keywords.keywords.length > 0">
          <p class="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-fg-faint">keywords</p>
          <span v-for="(keyword, index) in keywords.keywords" :key="index" class="inline-block mb-1.5 mr-1.5 rounded-full border border-line bg-surface px-2.5 py-0.5 text-xs text-fg">
          {{ keyword }}
        </span>
        </div>
      </div>

      <!-- Fact -->
      <div class="mt-4">
        <div v-if="factLoading" class="text-center">
          <LoadingState size="sm" label="llm is finding a fact" />
        </div>
        <div v-else-if="fact && fact.content" class="mt-4 p-3 rounded-xl" :style="{ backgroundColor: sdgColor }">
          <h3 class="text-lg font-semibold" :style="{ color: sdgColor !== '#A0A0A0' ? 'white' : 'gray' }">Did You Know?</h3>
          <p :style="{ color: sdgColor !== '#A0A0A0' ? 'white' : 'gray' }">{{ fact.content }}</p>
        </div>
      </div>

      <!-- Summary -->
      <div class="mt-4">
        <div v-if="summaryLoading" class="text-center">
          <LoadingState size="sm" label="llm is writing a summary" />
        </div>
        <div v-else-if="summary && summary.summary" class="mt-4">
          <p class="mb-1 font-mono text-[10px] uppercase tracking-wider text-fg-faint">summary</p>
          <p class="text-sm leading-relaxed text-fg">{{ summary.summary }}</p>
        </div>
      </div>

      <div class="p-4 mt-4">
        <UButton
          icon="mdi-tag-outline"
          size="lg"
          color="primary"
          variant="solid"
          :trailing="false"
          :block="true"
        >
          <NuxtLink :to="`/labeling/${selectedPublication.publicationId}`">Help us labeling this Publication</NuxtLink>
        </UButton>
      </div>
    </div>
  </div>

</template>


<script>
import { ref, watch, onMounted } from "vue";
import { usePublicationsStore } from "@/stores/publications";
import { useSDGsStore } from "~/stores/sdgs";
import { useGameStore } from "~/stores/game";
import usePublications from "@/composables/usePublications";

export default {
  setup() {
    const publicationsStore = usePublicationsStore();
    const gameStore = useGameStore();
    const sdgsStore = useSDGsStore();
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

          // Fetch data; each part shows as soon as it is there (a local LLM takes a while per part)
          keywords.value = await getPublicationKeywords(publicationId);
          keywordsLoading.value = false;
          fact.value = await getPublicationFact(publicationId);
          factLoading.value = false;
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

    // Get the currently selected SDG
    const currentSDG = computed(() => {
      const sdgId = gameStore.getSDG;
      return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
    });

    // Computed property to get the color of the selected SDG
    const sdgColor = computed(() => {
      return currentSDG.value ? sdgsStore.getColorBySDG(currentSDG.value.id) : "#525252"; // Default gray if no SDG
    });


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
      summaryLoading,
      currentSDG,
      sdgColor,
    };
  }
};
</script>

