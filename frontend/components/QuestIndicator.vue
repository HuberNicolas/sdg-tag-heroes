<template>
  <div class="flex items-start gap-2.5 w-full rounded-xl border border-line bg-surface-2/70 px-3 py-2 text-xs">
    <span class="quest-gem mt-0.5"><Icon :name="displayIcon" /></span>
    <div class="flex-1 min-w-0 leading-snug">
      <div class="flex items-center gap-2">
        <span class="font-mono text-[10px] uppercase tracking-wider text-fg-faint">quest</span>
        <span class="font-semibold text-fg">{{ name }}</span>
      </div>
      <p class="mt-0.5 text-fg-dim">{{ displayText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";

const labelDecisionsStore = useLabelDecisionsStore();
const selectedSDGLabelDecision = computed(() => labelDecisionsStore.selectedSDGLabelDecision);

const allButtons = [
  {
    icon: "i-heroicons-check-badge",
    name: "Confirm the King",
    tooltip: "Crown the most prominent instance: The majority of labels strongly favor one SDG, making it the clear winner.",
    condition: "Confirm"
  },
  {
    icon: "i-heroicons-map",
    name: "Explore",
    tooltip: "Look at a variety of predictions to explore uncertainty: Labels are spread across multiple SDGs, requiring a broader investigation of possibilities.",
    condition: "Explore"
  },
  {
    icon: "i-heroicons-magnifying-glass",
    name: "Investigate",
    tooltip: "Analyze and investigate data: The labels distribution is complex, with no clear consensus, requiring deeper analysis.",
    condition: "Investigate"
  },
  {
    icon: "i-heroicons-scale",
    name: "Tiebreaker",
    tooltip: "Resolve conflicts with a balanced approach: Two SDGs have received an equal number of labels, needing a decisive choice.",
    condition: "Tiebreaker"
  },
  {
    icon: "i-heroicons-user-group",
    name: "Decided",
    tooltip: "Community consensus achieved: The SDG has been successfully labeled through community voting process.",
    condition: "Decided"
  }
];

// Default quest message when no specific label distribution is present
const defaultQuest = {
  icon: "i-heroicons-question-mark-circle",
  name: "No Quest",
  tooltip: "No active scenario: There is currently no label distribution to evaluate."
};

// Get the active button details, or use default if none exists
const activeButton = computed(() => {
  const scenarioType = selectedSDGLabelDecision.value?.scenarioType;
  return allButtons.find(button => button.condition === scenarioType) || defaultQuest;
});

const displayText = computed(() => activeButton.value.tooltip);

const displayIcon = computed(() => activeButton.value.icon);

const name = computed(() => activeButton.value.name);
</script>
