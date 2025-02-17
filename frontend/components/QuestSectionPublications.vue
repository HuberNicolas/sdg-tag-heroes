<template>
  <div class="row-span-2 col-span-3">
    <div class="flex items-center justify-around">
      <QuestButtonExploration
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from "~/stores/game";
import QuestButtonExploration from "~/components/QuestButtonExploration.vue";

const gameStore = useGameStore();

const buttons = [
  /*
  { icon: "i-heroicons-check-badge", name: "Confirm the King", tooltip: "Crown the most prominent instance" },
  { icon: "i-heroicons-map", name: "Explore", tooltip: "Look at a variety of predictions to explore uncertainty" },
  { icon: "i-heroicons-magnifying-glass", name: "Investigate", tooltip: "Analyze and investigate data" },
  { icon: "i-heroicons-scale", name: "Tiebreaker", tooltip: "Resolve conflicts with a balanced approach" },
*/

  { icon: "i-heroicons-light-bulb", name: "Sparse Instances", tooltip: "Label an instance with the least annotations" },
  { icon: "i-heroicons-fire", name: "High Stakes", tooltip: "Sort the most uncertain instances based on entropy" },
];
</script>
