<template>
  <div class="flex items-start gap-2.5 w-full rounded-xl border border-line bg-surface-2/70 px-3 py-2 text-xs">
    <span class="quest-gem mt-0.5"><Icon :name="displayIcon" /></span>
    <div class="flex-1 min-w-0 leading-snug">
      <div class="flex items-center gap-2">
        <span class="font-mono text-[11px] uppercase tracking-wider text-fg-faint">quest</span>
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
    name: "Crown the Champion",
    tooltip: "One SDG has a clear majority of the votes. Check whether the majority is right.",
    condition: "Confirm"
  },
  {
    icon: "i-heroicons-map",
    name: "Mark the Map",
    tooltip: "The votes are spread over several SDGs. Read closely to find the best fit.",
    condition: "Explore"
  },
  {
    icon: "i-heroicons-magnifying-glass",
    name: "Solve the SDG Secret",
    tooltip: "Several SDGs are close and none leads. A careful look decides.",
    condition: "Investigate"
  },
  {
    icon: "i-heroicons-scale",
    name: "Decisive Duel",
    tooltip: "Two SDGs have the same number of votes. Your vote can break the tie.",
    condition: "Tiebreaker"
  },
  {
    icon: "i-heroicons-user-group",
    name: "Decided",
    tooltip: "The community has reached a decision on this publication.",
    condition: "Decided"
  }
];

// Default quest message when no specific label distribution is present
const defaultQuest = {
  icon: "i-heroicons-question-mark-circle",
  name: "No quest yet",
  tooltip: "There are not enough votes for a quest yet."
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
