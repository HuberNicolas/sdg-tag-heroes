<template>
  <div v-if="selectedSDGLabelDecision">
    <QuestButton
      v-if="selectedSDGLabelDecision.scenarioType === 'Confirm'"
      icon="i-heroicons-check-badge"
      name="Confirm the King"
      tooltip="Crown the most prominent instance"
    />

    <QuestButton
      v-else-if="selectedSDGLabelDecision.scenarioType === 'Explore'"
      icon="i-heroicons-map"
      name="Explore"
      tooltip="Look at a variety of predictions to explore uncertainty"
    />

    <QuestButton
      v-else-if="selectedSDGLabelDecision.scenarioType === 'Investigate'"
      icon="i-heroicons-magnifying-glass"
      name="Investigate"
      tooltip="Analyze and investigate data"
    />

    <QuestButton
      v-else-if="selectedSDGLabelDecision.scenarioType === 'Tiebreaker'"
      icon="i-heroicons-scale"
      name="Tiebreaker"
      tooltip="Resolve conflicts with a balanced approach"
    />

    <QuestButton
      v-else-if="selectedSDGLabelDecision.scenarioType === 'Not enough votes'"
      icon="question-mark-circle"
      name="Not enough votes"
      tooltip="Not enough votes"
    />
    <DecidedScenario />
  </div>
</template>

<script setup lang="ts">
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { computed } from "vue";

const labelDecisionsStore = useLabelDecisionsStore();

const selectedSDGLabelDecision = computed(() => labelDecisionsStore.selectedSDGLabelDecision);
const isLoading = computed(() => labelDecisionsStore.isLoading);
const error = computed(() => labelDecisionsStore.error);

</script>
