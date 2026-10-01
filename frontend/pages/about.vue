<template>
  <div class="px-4 py-10 lg:py-16">
    <div class="mx-auto max-w-5xl space-y-16">
      <!-- Intro -->
      <section class="grid items-center gap-10 md:grid-cols-[1.3fr_1fr]">
        <div class="space-y-5">
          <p class="kicker">// about the game</p>
          <h1 class="pixel gradient-text text-2xl leading-[1.4] lg:text-4xl">SDG Tag Heroes</h1>
          <p class="text-lg text-fg-dim">
            A gamified, collaborative platform for mapping scientific publications to the
            UN Sustainable Development Goals (SDGs).
          </p>
          <NuxtLink to="/scenarios" class="inline-block">
            <UButton size="lg" trailing-icon="i-mdi-arrow-right">Start playing</UButton>
          </NuxtLink>
        </div>
        <HoneycombMark class="mx-auto w-full max-w-xs" />
      </section>

      <!-- How it works -->
      <section class="space-y-5">
        <div>
          <p class="kicker">// 01 · loop</p>
          <h2 class="mt-2 text-2xl font-bold tracking-tight">How it works</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="(step, i) in steps" :key="step.title" class="about-card">
            <div class="flex items-center justify-between">
              <span class="hex-clip grid h-11 w-12 place-items-center bg-accent/15 text-accent">
                <Icon :name="step.icon" class="w-5 h-5" />
              </span>
              <span class="font-mono text-xs text-fg-faint">0{{ i + 1 }}</span>
            </div>
            <h3 class="mt-4 font-semibold">{{ step.title }}</h3>
            <p class="mt-1 text-sm text-fg-dim">{{ step.text }}</p>
          </div>
        </div>
      </section>

      <!-- Scenarios -->
      <section class="space-y-5">
        <div>
          <p class="kicker">// 02 · quests</p>
          <h2 class="mt-2 text-2xl font-bold tracking-tight">Quests</h2>
          <p class="mt-2 max-w-2xl text-fg-dim">
            Once enough votes are collected, a publication gets a quest that tells you what kind of help it needs.
          </p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="quest in quests" :key="quest.name" class="about-card">
            <h3 class="font-semibold">{{ quest.name }}</h3>
            <p class="mt-1 font-mono text-xs text-accent">votes {{ quest.split }}</p>
            <p class="mt-2 text-sm text-fg-dim">{{ quest.text }}</p>
          </div>
        </div>
      </section>

      <!-- Background -->
      <section class="about-card space-y-3 !p-6 lg:!p-8">
        <p class="kicker">// 03 · background</p>
        <h2 class="text-2xl font-bold tracking-tight">Background</h2>
        <p class="text-fg-dim">
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
.about-card {
  @apply rounded-[var(--radius)] border border-line bg-surface/80 p-5 backdrop-blur-sm transition-all duration-200;
  box-shadow: var(--shadow);
}
.about-card:hover {
  @apply -translate-y-0.5 border-line-strong;
}
</style>
