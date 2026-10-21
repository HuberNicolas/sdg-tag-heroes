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
import {useLabelDecisionsStore} from "~/stores/sdgLabelDecisions";
import {useGameStore} from "~/stores/game";
import { computed, ref } from "vue";
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
    required: false,
    default: undefined
  }
});

const isLoading = ref(false);
const error = ref<string | null>(null);

const dimensionalityStore = useDimensionalityReductionsStore();
const publicationsStore = usePublicationsStore();
const sdgPredictionsStore = useSDGPredictionsStore();
const labelDecisionsStore = useLabelDecisionsStore();
const gameStore = useGameStore();
const isActive = computed(() => gameStore.selectedScenarioList.includes(props.name));
const selectedSDG = gameStore.getSDG;

const scenarioMapping: Record<string, ScenarioType> = {
  "Crown the Champion": ScenarioType.CONFIRM,
  "Decisive Duel": ScenarioType.TIEBREAKER,
  "Solve the SDG Secret": ScenarioType.INVESTIGATE,
  "Mark the Map": ScenarioType.EXPLORE
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
