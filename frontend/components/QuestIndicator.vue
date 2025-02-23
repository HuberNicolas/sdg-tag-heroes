<template>
  <div class="flex items-center justify-between w-full text-xs space-x-2">
    <!-- Icon (Right-Aligned, Properly Positioned) -->
    <div class="w-6 h-6 flex items-center justify-center bg-primary-500 text-white
                transform rotate-45 relative shrink-0">
      <div class="absolute inset-0 bg-primary-500"></div>
      <div class="relative flex items-center justify-center w-4 h-4 bg-white rounded-full">
        <Icon
          :name="displayIcon"
          class="w-3 h-3 text-gray-700 transform -rotate-45"
        />
      </div>
    </div>

    <!-- Title & Text (Now Properly Left-Aligned) -->
    <div class="flex-1 text-left  leading-tight">
      <h3 class="font-semibold text-gray-800">Quest Indicator</h3>
      <span class="text-gray-700">{{name}}: {{ displayText }}</span>
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
