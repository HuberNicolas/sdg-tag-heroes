<template>
  <UTooltip :text="tooltip">
    <UButton
      size="sm"
      shape="round"
      :ui="{ base: 'ring-0', active: gameStore.isSelected(name) ? 'bg-primary-500 text-white' : '' }"
      @click="handleClick"
      :disabled="isLoading"
    >
      <template #default>
        <UAvatar v-if="!isLoading" :icon="icon" size="sm" />
        <span v-else>Loading...</span>
      </template>
    </UButton>
  </UTooltip>
</template>

<script setup lang="ts">
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useGameStore } from "~/stores/game";
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

// Updated scenario mapping
const scenarioMapping: Record<string, ScenarioType> = {
  "Confirm the King": ScenarioType.CONFIRM,
  "Tiebreaker": ScenarioType.TIEBREAKER,
  "Investigate": ScenarioType.INVESTIGATE,
  "Explore": ScenarioType.EXPLORE,

  "Sparse Instances": ScenarioType.SCARCE_LABELS, // New type for instances with few annotations
  "High Stakes": ScenarioType.HIGH_UNCERTAINTY // New type for cases with high entropy
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
      // Scenario was removed, reset arrays
      dimensionalityStore.scenarioTypeReductions = [];
      publicationsStore.scenarioTypePublications = [];
      sdgPredictionsStore.scenarioTypeSDGPredictions = [];
      labelDecisionsStore.scenarioTypeSDGLabelDecisions = [];
    } else {
      const scenarioType = scenarioMapping[props.name];

      if (props.name === "Sparse Instances") {
        // Fetch least-labeled data
        await dimensionalityStore.fetchLeastLabeledDimensionalityReductions(5);
        await publicationsStore.fetchLeastLabeledPublications(5);
        await sdgPredictionsStore.fetchLeastLabeledSDGPredictions(5);
        await labelDecisionsStore.fetchLeastLabeledSDGDecisions(5);
      } else if (props.name === "High Stakes") {
        // Fetch highest entropy data
        await dimensionalityStore.fetchMaxEntropyDimensionalityReductions(5);
        await publicationsStore.fetchMaxEntropyPublications(5);
        await sdgPredictionsStore.fetchMaxEntropySDGPredictions(5);
        await labelDecisionsStore.fetchMaxEntropySDGDecisions(5);
      } else {
        // Default behavior for other scenarios
      }
    }
  } catch (err) {
    error.value = `Error loading data: ${err}`;
  } finally {
    isLoading.value = false;
  }
};
</script>
