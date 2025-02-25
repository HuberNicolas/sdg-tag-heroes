<template>
  <div class="frame-container">
    <div class="frame-title"><b>by selecting</b> a Quest to Review Key Publications</div> <!--Smart Selection:  -->
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
import QuestButtonExploration from "~/components/QuestButtonExploration.vue";

const gameStore = useGameStore();

const buttons = [
  {
    icon: "i-heroicons-light-bulb",
    name: "Sparse Instances",
    tooltip: "Help review publications with the fewest labels",
    explanation: "These publications have received little attention and need more reviews to ensure accurate labeling."
  },
  {
    icon: "i-heroicons-fire",
    name: "High Stakes",
    tooltip: "Analyze publications where AI predictions are uncertain",
    explanation: "These publications show mixed AI predictions and need human insight to confirm the correct label."
  },
];

</script>
