<template>
  <div class="frame-container">
    <div class="frame-title"><b>by choosing</b> a <b>quest</b>: publications whose votes need a particular kind of help</div> <!--Guided Exploration: :  -->
    <div class="row-span-2 col-span-3">
      <div class="flex flex-wrap gap-2">
        <QuestButton
          v-for="button in buttons"
          :key="button.name"
          :icon="button.icon"
          :name="button.name"
          :tooltip="button.tooltip"
        />
      </div>
      <div v-if="gameStore.selectedScenarioList.length" class="flex items-center gap-2 mt-2.5">
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
        <span class="text-fg-dim text-xs leading-snug">{{ buttons.find(b => b.name === gameStore.selectedScenarioList[0])?.explanation }}</span>
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
    explanation: "One SDG has a clear majority of the votes. Check whether the majority is right."
  },
  {
    icon: "i-heroicons-map",
    name: "Mark the Map",
    tooltip: "Review diverse SDG label predictions",
    explanation: "The votes are spread over several SDGs: the model and the community are unsure. Read closely to find the best fit."
  },
  {
    icon: "i-heroicons-magnifying-glass",
    name: "Solve the SDG Secret",
    tooltip: "Analyze publications with conflicting labels",
    explanation: "Several SDGs are close and none leads. A careful look decides."
  },
  {
    icon: "i-heroicons-scale",
    name: "Decisive Duel",
    tooltip: "Decide between two equally labeled SDGs",
    explanation: "Two SDGs have the same number of votes. Your vote can break the tie."
  }
];

</script>
