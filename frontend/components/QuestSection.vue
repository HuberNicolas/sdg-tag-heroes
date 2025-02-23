<template>
  <div class="frame-container">
    <div class="frame-title"><b>Choose</b> among Quests to load new publications</div>
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
        <span class="text-gray-500 text-xs max-w-xs">{{ buttons.find(b => b.name === gameStore.selectedScenarioList[0])?.explanation }}</span>
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
    name: "Confirm the King",
    tooltip: "Crown the most prominent instance",
    explanation: "The majority of labels strongly favor one SDG, making it the clear winner."
  },
  {
    icon: "i-heroicons-map",
    name: "Explore",
    tooltip: "Look at a variety of predictions to explore uncertainty",
    explanation: "Labels are spread across multiple SDGs, requiring a broader investigation of possibilities."
  },
  {
    icon: "i-heroicons-magnifying-glass",
    name: "Investigate",
    tooltip: "Analyze and investigate data",
    explanation: "The labels distribution is complex, with no clear consensus, requiring deeper analysis."
  },
  {
    icon: "i-heroicons-scale",
    name: "Tiebreaker",
    tooltip: "Resolve conflicts with a balanced approach",
    explanation: "Two SDGs have received an equal number of labels, needing a decisive choice."
  }
];

</script>
