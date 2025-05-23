<template>
  <div class="relative group flex flex-col items-center w-full">
    <div class="mb-2 text-sm font-medium text-center">{{ name }}</div>
    <button
      class="w-8 h-8 flex items-center justify-center bg-primary-500 text-white rotate-45
             hover:bg-primary-600 active:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
      @click="handleClick"
      :disabled="isLoading"
    >
      <div class="absolute inset-0 bg-primary-500 rounded-md"></div>
      <div class="relative flex items-center justify-center w-6 h-6 bg-white rounded-full">
        <Icon
          v-if="!isLoading"
          :name="icon"
          class="w-4 h-4 text-gray-700 -rotate-45"
        />
        <span v-else class="text-xs text-gray-700 -rotate-45">Loading...</span>
      </div>
    </button>

    <span
      v-if="tooltip"
      class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover:opacity-100 transition-opacity"
    >
      {{ tooltip }}
    </span>
  </div>
</template>


<script setup lang="ts">
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useGameStore } from "~/stores/game";
import { ref, watch } from "vue";
import { ScenarioType } from "~/types/enums";

const props = defineProps({
  icon: { type: String, required: true },
  name: { type: String, required: true },
  tooltip: { type: String, required: false }
});

const isLoading = ref(false);
const error = ref<string | null>(null);

const gameStore = useGameStore();

const dimensionalityStore = useDimensionalityReductionsStore();
const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const labelDecisionsStore = useLabelDecisionsStore();

watch(
  () => gameStore.selectedScenarios,
  (newScenarios) => {
    if (!newScenarios?.includes(props.name)) {
      // Reset loading state when scenario is deselected
      isLoading.value = false;
    }
  }
);

const handleClick = async () => {
  isLoading.value = true;
  error.value = null;

  try {
    gameStore.toggleScenario(props.name);
    await handleScenarioSelection();
  } catch (err) {
    error.value = `Error loading data: ${err}`;
  } finally {
    isLoading.value = false;
  }
};

const handleScenarioSelection = async () => {
  if (!gameStore.selectedScenario) {
    // Scenario was deselected
    gameStore.clearScenarioData();
    return;
  }

  switch (gameStore.selectedScenario) {
    case "Hidden Gems":
      await Promise.all([
        dimensionalityStore.fetchLeastLabeledDimensionalityReductions(10),
        publicationsStore.fetchLeastLabeledPublications(10),
        sdgPredictionsStore.fetchLeastLabeledSDGPredictions(10),
        labelDecisionsStore.fetchLeastLabeledSDGDecisions(10),
      ]);
      break;

    case "High Stakes":
      await Promise.all([
        dimensionalityStore.fetchMaxEntropyDimensionalityReductions(10),
        publicationsStore.fetchMaxEntropyPublications(10),
        sdgPredictionsStore.fetchMaxEntropySDGPredictions(10),
        labelDecisionsStore.fetchMaxEntropySDGDecisions(10),
      ]);
      break;
  }
};
</script>
