<template>
  <div class="px-4 py-8 lg:py-12">
    <div class="mx-auto max-w-5xl space-y-10">
      <!-- Intro -->
      <section class="text-center space-y-3">
        <h1 class="press-start-font text-2xl lg:text-4xl">SDG Tag Heroes</h1>
        <p class="text-lg text-gray-700">
          A gamified, collaborative platform for mapping scientific publications to the
          UN Sustainable Development Goals (SDGs).
        </p>
        <NuxtLink to="/scenarios">
          <UButton size="lg" class="mt-2">Start playing</UButton>
        </NuxtLink>
      </section>

      <!-- How it works -->
      <section class="space-y-4">
        <h2 class="text-xl font-bold">How it works</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="step in steps" :key="step.title" class="frame-container bg-white">
            <Icon :name="step.icon" class="w-8 h-8 text-gray-700" />
            <h3 class="mt-2 font-semibold">{{ step.title }}</h3>
            <p class="text-sm text-gray-600">{{ step.text }}</p>
          </div>
        </div>
      </section>

      <!-- Scenarios -->
      <section class="space-y-4">
        <h2 class="text-xl font-bold">Quests</h2>
        <p class="text-gray-700">
          Once enough votes are collected, a publication gets a quest that tells you what kind of help it needs.
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="quest in quests" :key="quest.name" class="frame-container bg-white">
            <h3 class="font-semibold">{{ quest.name }}</h3>
            <p class="text-xs text-gray-500">Votes like {{ quest.split }}</p>
            <p class="mt-1 text-sm text-gray-600">{{ quest.text }}</p>
          </div>
        </div>
      </section>

      <!-- Background -->
      <section class="space-y-2">
        <h2 class="text-xl font-bold">Background</h2>
        <p class="text-gray-700">
          SDG Tag Heroes was built as part of a master's thesis at the University of Zurich (UZH). Machine-learning
          models predict which SDGs a publication addresses; players review the predictions, vote, annotate, and earn
          XP and coins. The SDG explanations and ground-truth labels come from SDG-Scout, an earlier project of the
          same research group.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const steps = [
  {
    icon: "mdi:map-search-outline",
    title: "Explore",
    text: "Pick an SDG world or a universe of publications and narrow them down on the publication map.",
  },
  {
    icon: "mdi:tag-outline",
    title: "Label",
    text: "Read the abstract with the machine's highlights and decide which SDG the publication contributes to.",
  },
  {
    icon: "mdi:account-group-outline",
    title: "Discuss",
    text: "Compare your label with the community, vote on others' labels, and earn XP and coins per SDG.",
  },
];

const quests = [
  { name: "Confirm", split: "6 / 4", text: "A clear favourite exists and needs confirmation." },
  { name: "Tiebreaker", split: "5 / 5", text: "Two SDGs are tied. Your vote decides." },
  { name: "Investigate", split: "3 / 3 / 3 / 1", text: "Votes are spread across several SDGs." },
  { name: "Explore", split: "1 / 2 / 2 / 2 / 1 …", text: "No agreement at all. Start from scratch." },
];
</script>

<style scoped>
.press-start-font {
  font-family: "Press Start 2P", monospace;
}
</style>
