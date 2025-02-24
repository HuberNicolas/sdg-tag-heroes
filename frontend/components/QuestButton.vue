<template>
  <div class="relative group flex flex-col items-center">
    <div class="mb-2 text-sm font-medium text-center">{{ name }}</div>
    <button
      class="w-12 h-12 flex items-center justify-center bg-primary-500 text-white rotate-45
             hover:bg-primary-600 active:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
      @click="handleClick"
      :disabled="isLoading"
    >
      <div class="absolute inset-0 bg-primary-500 rounded-md"></div>
      <div class="relative flex items-center justify-center w-10 h-10 bg-white rounded-full">
        <Icon
          v-if="!isLoading"
          :name="icon"
          class="w-6 h-6 text-gray-700 -rotate-45"
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
import {useLabelDecisionsStore} from "~/stores/sdgLabelDecisions";
import {useGameStore} from "~/stores/game";
import { ref } from "vue";
import { ScenarioType } from "~/types/enums";

const props = defineProps({
  icon: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  tooltip: {
    type: String,
    required: false
  }
});

const isLoading = ref(false);
const error = ref<string | null>(null);

const dimensionalityStore = useDimensionalityReductionsStore();
const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const labelDecisionsStore = useLabelDecisionsStore();
const gameStore = useGameStore();
const selectedSDG = gameStore.getSDG;

const scenarioMapping: Record<string, ScenarioType> = {
  "Confirm the King": ScenarioType.CONFIRM,
  "Tiebreaker": ScenarioType.TIEBREAKER,
  "Investigate": ScenarioType.INVESTIGATE,
  "Explore": ScenarioType.EXPLORE
};

const handleClick = async () => {
  isLoading.value = true;
  error.value = null;

  try {
    if (!selectedSDG) {
      throw new Error("No SDG selected.");
    }

    // Toggle scenario
    const previousScenario = gameStore.selectedScenario;
    gameStore.toggleScenario(props.name);

    if (previousScenario === props.name) {
      // Scenario was removed, directly reset arrays
      dimensionalityStore.scenarioTypeReductions = [];
      publicationsStore.scenarioTypePublications = [];
      sdgPredictionsStore.scenarioTypeSDGPredictions = [];
      labelDecisionsStore.scenarioTypeSDGLabelDecisions = [];
    } else {
      // Scenario was selected, fetch new data
      const scenarioType = scenarioMapping[props.name] || ScenarioType.NO_SPECIFIC_SCENARIO;

      await dimensionalityStore.fetchDimensionalityReductionsBySDGAndScenario(selectedSDG, "UMAP-15-0.0-2", scenarioType);
      await publicationsStore.fetchPublicationsForDimensionalityReductionsWithScenario(selectedSDG, "UMAP-15-0.0-2", scenarioType);
      await sdgPredictionsStore.fetchSDGPredictionsForDimensionalityReductionsWithScenario(selectedSDG, "UMAP-15-0.0-2", scenarioType);
      await labelDecisionsStore.fetchScenarioSDGLabelDecisionsForReduction(selectedSDG, "UMAP-15-0.0-2", scenarioType);
    }
  } catch (err) {
    error.value = `Error loading data: ${err}`;
  } finally {
    isLoading.value = false;
  }
};

</script>
