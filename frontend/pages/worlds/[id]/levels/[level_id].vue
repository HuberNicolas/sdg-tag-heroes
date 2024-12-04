<template>
  <div>
    <div>
      <MinimapContainer></MinimapContainer>
      <BoxplotContainer></BoxplotContainer>
    </div>
    <div>
      <p>{{ sdgId }} - {{ levelId }}</p>
      <UButton label="Back to Worlds Overview" @click="goBackToWorlds" />
      <UButton label="Back to World" @click="goBackToWorld" />

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
import { computed, ref, onMounted } from "vue";

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
const sdgStore = useSDGStore();

// State for reductions
const fetchingReductions = ref(false);
const errorReductions = ref<Error | null>(null);
const reductionsData = ref(null);

// State for publications
const fetchingPublications = ref(false);
const errorPublications = ref<Error | null>(null);
const publications = computed(() =>
  Object.values(publicationsStore.publications[sdgId]?.[levelId] || {})
);

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
