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
    case "Sparse Instances":
      await Promise.all([
        dimensionalityStore.fetchLeastLabeledDimensionalityReductions(5),
        publicationsStore.fetchLeastLabeledPublications(5),
        sdgPredictionsStore.fetchLeastLabeledSDGPredictions(5),
        labelDecisionsStore.fetchLeastLabeledSDGDecisions(5),
      ]);
      break;

    case "High Stakes":
      await Promise.all([
        dimensionalityStore.fetchMaxEntropyDimensionalityReductions(5),
        publicationsStore.fetchMaxEntropyPublications(5),
        sdgPredictionsStore.fetchMaxEntropySDGPredictions(5),
        labelDecisionsStore.fetchMaxEntropySDGDecisions(5),
      ]);
      break;
  }
};
</script>
