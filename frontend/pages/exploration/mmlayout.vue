<template>
  <div class="exploration-container">
    <h1>Exploration Page</h1>

    <!-- Options for Filtering -->
    <div class="options">
      <!-- SDG Input -->

      <UInputMenu
        v-model="selectedSDG"
        :options="sdgOptions"
        placeholder="Select an SDG Goal"
        by="id"
        option-attribute="name"
        :search-attributes="['name']"
      >
        <template #option="{ option: goal }">
          <!-- Render SDG Goal Name -->
          <span class="truncate">{{goal.id}} - {{ goal.name }}</span>
        </template>
      </UInputMenu>

      <!-- Limit Input -->
      <label>
        Limit:
        <input type="number" v-model.number="limit" min="1" />
      </label>

      <!-- Model Input -->
      <label>
        Model:
        <input type="text" v-model="model" placeholder="Enter model name or leave empty" />
      </label>

      <!-- SDG Range Inputs -->
      <label>
        SDG Range Min:
        <input type="number" v-model.number="sdgRange[0]" step="0.01" />
      </label>
      <label>
        SDG Range Max:
        <input type="number" v-model.number="sdgRange[1]" step="0.01" />
      </label>
    </div>

    <!-- Loading Indicator with Spinner -->
    <div v-if="publicationStore.loading" class="loading">
      <span class="spinner"></span> Loading publications...
    </div>

    <!-- Error Message -->
    <div v-if="publicationStore.error" class="error">{{ publicationStore.error }}</div>

    <!-- Minimap and Boxplot Components with Publications Data Passed as Props -->
    <MinimapContainer :publications="publicationStore.publications"></MinimapContainer>
    <BoxplotContainer :publications="publicationStore.publications"></BoxplotContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { debounce } from 'lodash-es';
import MinimapContainer from '~/components/MinimapContainer.vue';
import BoxplotContainer from '~/components/BoxplotContainer.vue';
import { usePublicationStore } from "~/stores/publications";
import {useSDGStore} from "~/stores/sdgs";
import PublicationService from '@/composables/usePublication';
import UseSDGGoals from "@/composables/useSDGs";


// Setup the store and service
const publicationStore = usePublicationStore();
const publicationService = new PublicationService();
const sdgStore = useSDGStore();
const sdgGoalsService = new UseSDGGoals(); // Instantiate UseSDGGoals

// Selected SDG goal
const selectedSDG = ref( null); //

// Computed property for the SDG options
const sdgOptions = computed(() =>
  sdgStore.sdgGoals.map(goal => ({
    id: goal.id, // Assuming the SDG goal has an 'id' field
    name: goal.name, // Assuming the SDG goal has a 'name' field
    colors: goal.colors, // Assuming the SDG goal has a 'colors' array
    icon: goal.icon // Assuming the SDG goal has an 'icon' as an encoded SVG string
  }))
);

// Watch effect to check if SDG goals are loaded and set the default selection
watchEffect(() => {
  if (sdgStore.sdgGoals.length > 0 && !selectedSDG.value) {
    selectedSDG.value = sdgOptions.value[0] || null;
  }
});

// Load SDG goals if not already loaded
if (!sdgStore.sdgGoals.length) {
  sdgStore.loadSDGGoals(async () => {
    // Provide your fetching logic here, for example:
    const useSDGGoals = new (await import('@/composables/useSDGs')).default();
    return useSDGGoals.getSDGGoals();
  });
}


// Options for Filtering
const limit = ref<number>(10);
const model = ref<string | null>(null);
const sdgRange = ref<[number, number]>([0.98, 0.99]);


// Function to fetch and store publications
const fetchAndStorePublications = async () => {
  const sdgIds = selectedSDG.value ? [selectedSDG.value.id] : []; // Include the selected SDG ID if available
  await publicationStore.loadPublications(() =>
    publicationService.getPublicationsBySDGValues(
      sdgRange.value, // SDG range
      limit.value, // Limit
      sdgIds, // SDGs to filter (customize as needed)
      [], // No includes needed
      model.value // Model name (or null if not specified)
    )
  );
};


// Function to fetch SDG goals (only once)
const fetchSDGGoals = async () => {
  try {
    await sdgStore.loadSDGGoals(() => sdgGoalsService.getSDGGoals());
  } catch (error) {
    console.error("Error fetching SDG goals:", error);
  }
};


// Debounced fetch function to avoid excessive API calls
const debouncedFetch = debounce(fetchAndStorePublications, 300);

// Automatically fetch publications on page load
onMounted(() => {
  fetchSDGGoals(); // Fetch SDG goals once
  fetchAndStorePublications();
});

// Watch for changes in filters and refetch publications
watch([limit, model, sdgRange], () => {
  debouncedFetch();
});
</script>

<style scoped>
.exploration-container {
  max-width: 1200px;
  margin: auto;
  padding: 20px;
}

.options {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
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
