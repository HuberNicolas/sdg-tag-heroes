<template>
  <div class="flex flex-col items-center justify-center">
    <p class="kicker mb-4 self-start xl:self-center">// choose a universe</p>

    <!-- Stepper: one hexagon per universe -->
    <ol class="flex w-full max-w-md items-center">
      <template v-for="level in levels" :key="level.level">
        <li class="flex-none">
          <button
            type="button"
            class="hex-step"
            :class="[getStepClass(level.level), { 'hex-step--active': selectedLevel === level.level }]"
            :aria-label="`Universe ${level.level}`"
            @click="selectLevel(level.level)"
          >
            <span class="hex-clip hex-step__shape">{{ level.level }}</span>
          </button>
        </li>
        <li
          v-if="level.level < levels.length"
          class="mx-2 h-px flex-1"
          :class="isLevelUnlocked(level.level + 1) ? 'bg-accent/60' : 'bg-line-strong'"
          aria-hidden="true"
        />
      </template>
    </ol>

    <div class="grid grid-cols-3 gap-3 lg:gap-4 2xl:gap-6 mt-6 w-full max-w-3xl">
      <div
        v-for="(level, index) in levels"
        :key="index"
        class="col-span-1 cursor-pointer"
        @click="selectLevel(level.level)"
      >
        <div
          class="universe-card"
          :class="{ 'universe-card--active': selectedLevel === level.level, 'universe-card--locked': !isLevelUnlocked(level.level) }"
        >
          <div class="font-mono text-[11px] text-fg-faint">universe_0{{ level.level }}</div>
          <div class="mt-2 text-[10px] xl:text-xs 2xl:text-sm text-fg press-start-font leading-relaxed">{{ level.name }}</div>
          <div class="mt-2 flex items-center gap-1.5 font-mono text-[11px]">
            <template v-if="!isLevelUnlocked(level.level)">
              <Icon name="mdi-lock-outline" class="text-fg-faint" /><span class="text-fg-dim">Almost There!</span>
            </template>
            <template v-else>
              <span class="h-1.5 w-1.5 rounded-full bg-accent shadow-[0_0_8px_rgb(var(--c-accent))]" /><span class="text-accent">Ready to play</span>
            </template>
          </div>
          <div v-if="shouldShowProgress(level.level)" class="mt-4 w-full">
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted-strong">
              <div class="h-full rounded-full bg-gradient-to-r from-accent to-hero-blue transition-[width] duration-700" :style="{ width: getProgress(level.level) + '%' }" />
            </div>
            <div class="mt-1.5 font-mono text-[10px] text-fg-dim text-right">
              <span v-if="isLevelUnlocked(level.level)">
                {{ Math.round(userXP) }} XP
              </span>
              <span v-else>
                {{ Math.round(userXP) }} / {{ level.requiredXP }} XP
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedLevel" class="mt-6 w-full max-w-md 2xl:max-w-lg">
      <div class="world-card">
        <figure class="relative">
          <img :src="selectedWorld.image" alt="World Image" class="w-full max-h-[30vh] object-cover" >
          <div class="absolute inset-0 bg-gradient-to-t from-surface via-surface/20 to-transparent" />
        </figure>
        <div class="relative -mt-12 p-5 pt-0">
          <p class="kicker">// universe_0{{ selectedWorld.level }}</p>
          <h2 class="mt-2 text-lg text-fg press-start-font">{{ selectedWorld.name }}</h2>
          <p class="mt-2 text-sm text-fg-dim">{{ selectedWorld.description }}</p>
          <!-- Play Button -->
          <UButton
            v-if="isLevelUnlocked(selectedLevel)"
            :color="'primary'"
            :variant="'solid'"
            size="lg"
            block
            trailing-icon="i-mdi-arrow-right"
            class="mt-4"
            @click="playWorld"
          >
            Play {{ selectedWorld.name }}
          </UButton>

          <!-- Locked Button -->
          <UButton
            v-else
            :color="'primary'"
            :variant="'solid'"
            size="lg"
            block
            icon="i-mdi-lock-outline"
            :disabled="true"
            class="mt-4"
          >
            Almost There!
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useXPBanksStore } from "~/stores/xpBanks";
import { useGameStore } from "~/stores/game";
import { computed, ref } from "vue";

const router = useRouter();
const banksStore = useXPBanksStore();
const gameStore = useGameStore();

const userXP = computed(() => banksStore.getUserXPBank?.totalXp || 0);
const selectedLevel = ref<number>(1);

const levels = [
  { level: 1, name: "Researchia", bgColor: "bg-gray-400", borderClass: "border-line-strong", requiredXP: 0, description: "Find discovery and innovation.", image: "/img/world-1.png" },
  { level: 2, name: "PubliVerse", bgColor: "bg-gray-500", borderClass: "border-line-strong", requiredXP: 6000, description: "Filled with academic publications.", image: "/img/world-2.png" },
  { level: 3, name: "Revealo", bgColor: "bg-gray-600", borderClass: "border-line-strong", requiredXP: 8000, description: "Open knowledge and revelations.", image: "/img/world-3.png" },
];

const isLevelUnlocked = (level: number) => {
  const requiredXP = levels.find(l => l.level === level)?.requiredXP || 0;
  return userXP.value >= requiredXP;
};

const shouldShowProgress = (_level: number) => {
  //const nextLevel = levels.find(l => l.requiredXP > userXP.value);
  //return nextLevel?.level === level;
  return true
};

const getProgress = (level: number) => {
  const requiredXP = levels.find(l => l.level === level)?.requiredXP || 0;
  if (requiredXP === 0) return 100; // Fully unlocked
  return requiredXP > 0 ? Math.min((userXP.value / requiredXP) * 100, 100) : 0;
};

const selectLevel = (level: number) => {
  selectedLevel.value = level;
};

const playWorld = () => {
  if (isLevelUnlocked(selectedLevel.value)) {
    gameStore.setLevel(selectedLevel.value);
    router.push(`/exploration/publications/${selectedLevel.value}`);
  }
};

const getStepClass = (level: number) => {
  return isLevelUnlocked(level) ? "hex-step--unlocked" : "hex-step--locked";
};

const selectedWorld = computed(() => {
  return levels.find(l => l.level === selectedLevel.value) || levels[0];
});
</script>



<style scoped>
.press-start-font {
  font-family: var(--font-pixel);
}

.hex-step__shape {
  @apply grid h-10 w-11 place-items-center font-mono text-sm font-semibold transition-all duration-200;
}
.hex-step--unlocked .hex-step__shape {
  @apply bg-accent/15 text-accent;
}
.hex-step--locked .hex-step__shape {
  @apply bg-muted text-fg-dim;
}
.hex-step--active .hex-step__shape {
  @apply bg-accent text-surface;
}
.hex-step:hover .hex-step__shape {
  @apply scale-110;
}

.universe-card {
  @apply relative flex h-full flex-col rounded-[var(--radius)] border border-line bg-surface/80 p-4 backdrop-blur-sm transition-all duration-200;
  box-shadow: var(--shadow);
}
.universe-card:hover {
  @apply -translate-y-0.5 border-line-strong;
}
.universe-card--active {
  @apply border-accent/60;
  box-shadow: 0 0 0 1px rgb(var(--c-accent) / 0.4), 0 12px 32px -12px rgb(var(--c-accent) / 0.35);
}
.universe-card--locked {
  @apply opacity-80;
}

.world-card {
  @apply overflow-hidden rounded-[18px] border border-line bg-surface;
  box-shadow: var(--shadow);
}
</style>
