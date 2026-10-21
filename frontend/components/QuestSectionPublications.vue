<template>
  <div class="frame-container">
    <div class="frame-title"><b>by choosing</b> a <b>quest</b>: publications that need attention most</div> <!--Smart Selection:  -->
    <div class="row-span-2 col-span-3">
      <div class="flex flex-wrap gap-2">
        <QuestButtonExploration
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
import QuestButtonExploration from "~/components/QuestButtonExploration.vue";

const gameStore = useGameStore();

const buttons = [
  {
    icon: "i-heroicons-light-bulb",
    name: "Hidden Gems",
    tooltip: "Publications with the fewest labels so far",
    explanation: "These publications have few labels yet, so each new label carries more weight."
  },
  {
    icon: "i-heroicons-fire",
    name: "High Stakes",
    tooltip: "Publications where the model is most uncertain",
    explanation: "The model's scores are spread over several SDGs (high entropy); a human reading helps most here."
  },
];

</script>
