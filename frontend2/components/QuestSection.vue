<template>
  <div class="frame-container">
    <div class="frame-title"><b>by selecting</b> a Quest to explore Publications with Unique Label Patterns from the <b>Quest Box</b></div> <!--Guided Exploration: :  -->
    <div class="row-span-2 col-span-3">
      <div class="flex items-center justify-around">
        <QuestButton
          v-for="button in buttons"
          :key="button.name"
          :icon="button.icon"
          :name="button.name"
          :tooltip="button.tooltip"
        />
      </div>
      <div class="flex gap-2 mt-4">
        <UBadge
          v-for="scenario in gameStore.selectedScenarioList"
          :key="scenario"
          size="xs"
          color="primary"
          variant="solid"
        >
          <template #leading>
            <UIcon :name="buttons.find(b => b.name === scenario)?.icon" class="w-4 h-4" />
          </template>
          {{ scenario }}
          <template #trailing>
            <UButton size="xs" icon="i-heroicons-x-mark" @click="gameStore.removeScenario(scenario)" />
          </template>
        </UBadge>
        <span class="text-gray-500 text-xs">{{ buttons.find(b => b.name === gameStore.selectedScenarioList[0])?.explanation }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from "~/stores/game";
import QuestButton from "~/components/QuestButton.vue";

const gameStore = useGameStore();

const buttons = [
  {
    icon: "i-heroicons-check-badge",
    name: "Crown the Champion",
    tooltip: "Validate the strongest SDG label",
    explanation: "This publication has a dominant SDG label, widely agreed upon. Confirm if the majority label is correct."
  },
  {
    icon: "i-heroicons-map",
    name: "Mark the Map",
    tooltip: "Review diverse SDG label predictions",
    explanation: "This publication has a mix of SDG labels, meaning the AI and users are uncertain. Broaden your investigation to find the best fit."
  },
  {
    icon: "i-heroicons-magnifying-glass",
    name: "Solve the SDG Secret",
    tooltip: "Analyze publications with conflicting labels",
    explanation: "This publication has multiple SDGs with no clear leader. Investigate deeper to determine the most fitting SDG."
  },
  {
    icon: "i-heroicons-scale",
    name: "Decisive Duel",
    tooltip: "Decide between two equally labeled SDGs",
    explanation: "This publication has an equal number of votes for two SDGs. Help break the tie by analyzing the content and selecting the best fit."
  }
];

</script>
