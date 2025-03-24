<template>
  <div class="flex flex-col items-center justify-center">
    <ul class="steps">
      <li data-content="1" class="step" :class="getStepClass(1)" @click="selectLevel(1)"></li>
      <li data-content="2" class="step" :class="getStepClass(2)" @click="selectLevel(2)"></li>
      <li data-content="3" class="step" :class="getStepClass(3)" @click="selectLevel(3)"></li>
    </ul>
    <div class="grid grid-cols-3 gap-12 mt-6">
      <div
        v-for="(level, index) in levels"
        :key="index"
        class="col-span-1 cursor-pointer"
        @click="selectLevel(level.level)"
      >
        <div
          :class="`relative flex flex-col items-center justify-center rounded-lg border-4 p-4 shadow-lg ${level.borderClass} bg-white`"
        >
          <div class="text-lg font-bold text-gray-800">Universe {{ level.level }}</div>
          <div class="text-lg font-bold text-gray-800 press-start-font">{{ level.name }}</div>
          <div v-if="!isLevelUnlocked(level.level)" class="font-semibold">Almost There!</div>
          <div v-else class="font-semibold">Ready to play</div>
          <div v-if="shouldShowProgress(level.level)" class="w-full bg-gray-300 rounded-md mt-4">
            <div class="bg-gray-500 text-xs text-white text-center rounded-md p-2" :style="{ width: getProgress(level.level) + '%' }">
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
    <div v-if="selectedLevel" class="mt-6 w-96">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title press-start-font">{{ selectedWorld.name }}</h2>
          <p>{{ selectedWorld.description }}</p>
          <!-- Play Button -->
          <UButton
            v-if="isLevelUnlocked(selectedLevel)"
            @click="playWorld"
            :color="'primary'"
            :variant="'solid'"
            class="mt-4"
          >
            Play {{ selectedWorld.name }}
          </UButton>

          <!-- Locked Button -->
          <UButton
            v-else
            :color="'primary'"
            :variant="'solid'"
            :disabled="true"
            class="mt-4"
          >
            Almost There!
          </UButton>
        </div>
        <figure>
          <img :src="selectedWorld.image" alt="World Image" />
        </figure>
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
  { level: 1, name: "Researchia", bgColor: "bg-gray-400", borderClass: "border-gray-600", requiredXP: 0, description: "Find discovery and innovation.", image: "/img/world-1.png" },
  { level: 2, name: "PubliVerse", bgColor: "bg-gray-500", borderClass: "border-gray-600", requiredXP: 6000, description: "Filled with academic publications.", image: "/img/world-2.png" },
  { level: 3, name: "Revealo", bgColor: "bg-gray-600", borderClass: "border-gray-600", requiredXP: 8000, description: "Open knowledge and revelations.", image: "/img/world-3.png" },
];

const isLevelUnlocked = (level: number) => {
  const requiredXP = levels.find(l => l.level === level)?.requiredXP || 0;
  return userXP.value >= requiredXP;
};

const shouldShowProgress = (level: number) => {
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
  return isLevelUnlocked(level) ? "step-neutral" : "step-disabled text-gray-400";
};

const selectedWorld = computed(() => {
  return levels.find(l => l.level === selectedLevel.value) || levels[0];
});
</script>



<style scoped>
.press-start-font {
  font-family: "Press Start 2P", monospace;
}
</style>
