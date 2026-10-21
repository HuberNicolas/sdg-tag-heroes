<template>
  <!-- Quest: a compact pill with a small diamond (quest publications are diamonds on the map) -->
  <button
    type="button"
    class="quest-pill"
    :class="{ 'is-active': isActive }"
    :disabled="isLoading"
    :title="tooltip"
    :aria-pressed="isActive"
    @click="handleClick"
  >
    <span class="quest-pill__gem">
      <Icon v-if="!isLoading" :name="icon" class="quest-pill__icon" />
      <LoadingState v-else size="sm" label="" class="!p-0 scale-75" />
    </span>
    <span class="truncate">{{ name }}</span>
  </button>
</template>


<script setup lang="ts">
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useGameStore } from "~/stores/game";
import { computed, ref, watch } from "vue";

const props = defineProps({
  icon: { type: String, required: true },
  name: { type: String, required: true },
  tooltip: { type: String, required: false, default: undefined }
});

const isLoading = ref(false);
const error = ref<string | null>(null);

const gameStore = useGameStore();
const isActive = computed(() => gameStore.selectedScenarioList.includes(props.name));

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
