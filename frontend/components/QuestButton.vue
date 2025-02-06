<template>
  <UTooltip :text="tooltip">
    <UButton
      size="md"
      shape="round"
      :ui="{ base: 'ring-0' }"
      @click="handleClick"
      :disabled="isLoading"
    >
      <template #default>
        <UAvatar v-if="!isLoading" :icon="icon" size="xl" />
        <span v-else>Loading...</span>
      </template>
    </UButton>
  </UTooltip>
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

    const scenarioType = scenarioMapping[props.name] || ScenarioType.NO_SPECIFIC_SCENARIO;

    await dimensionalityStore.fetchDimensionalityReductionsBySDGAndScenario(selectedSDG, "UMAP-15-0.0-2", scenarioType);
    await publicationsStore.fetchPublicationsForDimensionalityReductionsWithScenario(selectedSDG, "UMAP-15-0.0-2", scenarioType);
    await sdgPredictionsStore.fetchSDGPredictionsForDimensionalityReductionsWithScenario(selectedSDG, "UMAP-15-0.0-2", scenarioType);
    await labelDecisionsStore.fetchScenarioSDGLabelDecisionsForReduction(selectedSDG, "UMAP-15-0.0-2", scenarioType);

  } catch (err) {
    error.value = `Error loading data: ${err}`;
  } finally {
    isLoading.value = false;
  }
};
</script>
