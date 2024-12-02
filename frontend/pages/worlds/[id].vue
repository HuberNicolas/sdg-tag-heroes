<template>
  <div class="flex flex-col h-screen p-4">
    <header class="flex justify-between items-start">
      <h1 class="text-2xl font-bold mb-4">Sustainable Development Goal</h1>
      <div class="w-1/3">
        <UCard
          v-if="goal"
          class="aspect-square flex flex-col items-center justify-between text-center shadow-lg rounded-lg overflow-hidden"
          :style="{ border: `4px solid ${goal.color}` }"
        >
          <template #header>
            <h2 class="text-lg font-bold mb-2" :style="{ color: goal.color }">{{ goal.name }}</h2>
          </template>
          <img
            v-if="goal.icon"
            :src="`data:image/svg+xml;base64,${goal.icon}`"
            :alt="goal.name"
            class="w-full h-full object-contain"
          />
          <template #footer>
            <p class="text-sm mt-4">Goal {{ goal.index }}</p>
          </template>
        </UCard>
      </div>
    </header>

    <main class="flex-grow mt-6">
      <div v-if="error" class="text-red-500">Error: {{ error.message }}</div>
      <div v-else-if="pending" class="text-center">Loading...</div>
      <div v-else>
        <p class="text-lg mb-4">Description:</p>
        <ul class="list-disc list-inside">
          <li v-for="target in goal.sdg_targets" :key="target.id">
            <span class="font-bold">{{ target.index }}</span> - {{ target.text }}
          </li>
        </ul>

        <UButton label="Back to Worlds" @click="goBack" />

        <!-- Levels Section -->
        <!-- Levels Section -->
        <div class="mt-10">
          <h2 class="text-xl font-bold mb-6">Achievement Levels</h2>
          <div class="flex justify-center gap-4">
            <!-- Bronze Level -->
            <UCard
              class="flex flex-col items-center justify-center text-center shadow-lg rounded-lg overflow-hidden w-1/4 aspect-square"
              :style="{ border: '4px solid #cd7f32' }"
            >
              <template #header>
                <h3 class="text-lg font-bold mb-2 text-[#cd7f32]">Bronze</h3>
              </template>
              <p v-if="levelData[1]">
                {{ levelData[1].reductions?.[`sdg${route.params.id}`]?.level1?.length || 0 }}
                items retrieved for Level 1.
              </p>
              <p v-else>No data found for Bronze level.</p>
            </UCard>

            <!-- Silver Level -->
            <UCard
              class="flex flex-col items-center justify-center text-center shadow-lg rounded-lg overflow-hidden w-1/4 aspect-square"
              :style="{ border: '4px solid #c0c0c0' }"
            >
              <template #header>
                <h3 class="text-lg font-bold mb-2 text-[#c0c0c0]">Silver</h3>
              </template>
              <p v-if="levelData[2]">
                {{ levelData[2].reductions?.[`sdg${route.params.id}`]?.level2?.length || 0 }}
                items retrieved for Level 2.
              </p>
              <p v-else>No data found for Silver level.</p>
            </UCard>

            <!-- Gold Level -->
            <UCard
              class="flex flex-col items-center justify-center text-center shadow-lg rounded-lg overflow-hidden w-1/4 aspect-square"
              :style="{ border: '4px solid #ffd700' }"
            >
              <template #header>
                <h3 class="text-lg font-bold mb-2 text-[#ffd700]">Gold</h3>
              </template>
              <p v-if="levelData[3]">
                {{ levelData[3].reductions?.[`sdg${route.params.id}`]?.level3?.length || 0 }}
                items retrieved for Level 3.
              </p>
              <p v-else>No data found for Gold level.</p>
            </UCard>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useAsyncData } from "#app";
import { useRuntimeConfig } from "nuxt/app";
import { SDGGoal } from "~/types/sdg/goals";
import { DimensionalityReductionResponse } from "~/types/dimensionalityReduction";

const route = useRoute();
const router = useRouter();
const config = useRuntimeConfig();

const { data: goalData, pending: goalPending, error: goalError } = await useAsyncData<SDGGoal>(
  `sdgGoal-${route.params.id}`,
  async () => {
    const response = await $fetch<SDGGoal>(
      `${config.public.apiUrl}sdgs/${route.params.id}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      }
    );
    return response;
  }
);

const goal = goalData?.value || null;

const levels = [1, 2, 3]; // Bronze = 1, Silver = 2, Gold = 3
const levelData = ref<Record<number, DimensionalityReductionResponse | null>>({
  1: null,
  2: null,
  3: null,
});

const levelFetching = ref(false); // Separate pending state for level data
const levelError = ref<Error | null>(null); // Separate error for level data

const fetchLevels = async () => {
  levelFetching.value = true;
  levelError.value = null; // Reset error state before fetching
  try {
    const sdgId = route.params.id; // SDG ID from the route
    const fetchPromises = levels.map((level) =>
      $fetch<DimensionalityReductionResponse>(
        `${config.public.apiUrl}dimensionality_reductions?sdg=${sdgId}&level=${level}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      )
    );

    // Fetch all levels concurrently
    const results = await Promise.all(fetchPromises);

    // Map results to levels
    results.forEach((result, index) => {
      levelData.value[levels[index]] = result;
    });
  } catch (err) {
    levelError.value = err as Error;
    console.error("Error fetching levels:", err);
  } finally {
    levelFetching.value = false;
  }
};

// Fetch data on mount
onMounted(() => {
  fetchLevels();
});

// Navigate back
const goBack = () => {
  router.push("/worlds");
};
</script>


<style scoped>
header {
  position: relative;
}

main {
  overflow-y: auto;
}

img {
  object-fit: contain;
  margin: auto;
}

.flex {
  display: flex;
}

.gap-4 {
  gap: 1rem;
}

.mt-10 {
  margin-top: 2.5rem;
}
</style>
