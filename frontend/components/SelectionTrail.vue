<template>
  <!-- Provenance of the current selection: which steps led to the publications in the summary and the table -->
  <nav class="flex min-w-0 flex-wrap items-center gap-1 font-mono text-[11px]" aria-label="How this selection was made">
    <template v-for="(step, index) in steps" :key="step.key">
      <span v-if="index > 0" class="text-fg-faint" aria-hidden="true">›</span>
      <span class="trail-step" :class="{ 'is-empty': step.empty }" :title="step.title">
        <Icon :name="step.icon" class="h-3 w-3 flex-none text-accent" />{{ step.label }}
        <button
          v-if="step.clear"
          type="button"
          class="ml-0.5 text-fg-faint hover:text-hero-red"
          :aria-label="`Remove ${step.label}`"
          @click="step.clear"
        >✕</button>
      </span>
    </template>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useGameStore } from "~/stores/game";
import { useCollectionsStore } from "~/stores/collections";
import { usePublicationsStore } from "~/stores/publications";

const route = useRoute();
const gameStore = useGameStore();
const collectionsStore = useCollectionsStore();
const publicationsStore = usePublicationsStore();
const { topSdgFilter, clearTopSdgFilter } = useTopSdgFilter();

type Step = { key: string; icon: string; label: string; title: string; empty?: boolean; clear?: () => void };

const steps = computed<Step[]>(() => {
  const list: Step[] = [];
  const level = gameStore.getLevel;
  if (route.path.startsWith("/exploration/sdgs/") && gameStore.getSDG) {
    list.push({ key: "map", icon: "mdi-hexagon-outline", label: `SDG ${gameStore.getSDG} world · level ${level}`, title: "Map: publications of one SDG world" });
  } else {
    list.push({ key: "map", icon: "mdi-hexagon-outline", label: `universe_0${level ?? "?"}`, title: "Map: one part of the publication map" });
  }

  const selectedTopics = collectionsStore.selectedCollections.length;
  const allTopics = collectionsStore.collections.length;
  list.push({
    key: "topics",
    icon: "mdi-tag-multiple-outline",
    label: selectedTopics === 0 ? "no topic" : selectedTopics >= allTopics ? "all topics" : `${selectedTopics} topic${selectedTopics > 1 ? "s" : ""}`,
    title: "Topics shown on the map",
    empty: selectedTopics === 0,
  });

  const quest = gameStore.selectedScenarioList?.[0];
  if (quest) list.push({ key: "quest", icon: "mdi-rhombus-outline", label: `quest: ${quest}`, title: "Quest publications added to the map" });

  if (gameStore.getUserCoordinates) list.push({ key: "poi", icon: "mdi-map-marker-outline", label: "your POI", title: "Point of interest from the query box" });

  const selected = publicationsStore.selectedPartitionedPublications?.length ?? 0;
  list.push({
    key: "selection",
    icon: "mdi-lasso",
    label: selected ? `selected: ${selected}` : "nothing selected",
    title: "Publications selected on the map (lasso or click)",
    empty: !selected,
  });

  if (topSdgFilter.value) {
    list.push({ key: "filter", icon: "mdi-filter-outline", label: `top SDG ${topSdgFilter.value}`, title: "Table filtered by top SDG", clear: clearTopSdgFilter });
  }
  return list;
});
</script>

<style scoped>
.trail-step {
  @apply inline-flex items-center gap-1 whitespace-nowrap rounded-full border border-line bg-surface/70 px-2 py-0.5 text-fg-dim;
}
.trail-step.is-empty {
  @apply border-dashed text-fg-faint;
}
</style>
