<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="col-span-2"><div class="flex justify-center gap-4">
      <div><UCard
        v-if="goal"
        class="aspect-square flex flex-col items-center justify-between text-center shadow-lg rounded-lg overflow-hidden"
        :style="{ border: `4px solid ${goal.color}` }"
      >
        <template #header>
          <h2 class="text-lg font-bold mb-2" :style="{ color: goal.color }">Goal {{ goal.index }} - {{ goal.name }}</h2>
        </template>
        <img
          v-if="goal.icon"
          :src="`data:image/svg+xml;base64,${goal.icon}`"
          :alt="goal.name"
          class="w-1/2 h-1/2 object-contain"
        />
      </UCard>
      </div>
      <!-- Bronze Level -->
      <UCard
        class="flex flex-col items-center justify-center text-center shadow-lg rounded-lg overflow-hidden w-1/4 aspect-square"
        :style="{ border: '4px solid #cd7f32' }"
      >
        <template #header>
          <h3 class="text-lg font-bold mb-2 text-[#cd7f32]">Bronze</h3>
        </template>
        <p v-if="levelData?.levels?.[1]?.reductions?.length">
          {{ levelData.levels[1].reductions.length }} items retrieved for Level 1.
        </p>
        <p v-else>No data found for Bronze level.</p>
        <NuxtLink :to="{ name: 'worlds-id-levels-level_id', params: { id:sdgId , level_id: 1 }}">
          <p>Play</p>
        </NuxtLink>
      </UCard>

      <!-- Silver Level -->
      <UCard
        class="flex flex-col items-center justify-center text-center shadow-lg rounded-lg overflow-hidden w-1/4 aspect-square"
        :style="{ border: '4px solid #c0c0c0' }"
      >
        <template #header>
          <h3 class="text-lg font-bold mb-2 text-[#c0c0c0]">Silver</h3>
        </template>
        <p v-if="levelData?.levels?.[2]?.reductions?.length">
          {{ levelData.levels[2].reductions.length }} items retrieved for Level 2.
        </p>
        <p v-else>No data found for Silver level.</p>
        <NuxtLink :to="{ name: 'worlds-id-levels-level_id', params: { id:sdgId , level_id: 2 }}">
          <p>Play</p>
        </NuxtLink>
      </UCard>

      <!-- Gold Level -->
      <UCard
        class="flex flex-col items-center justify-center text-center shadow-lg rounded-lg overflow-hidden w-1/4 aspect-square"
        :style="{ border: '4px solid #ffd700' }"
      >
        <template #header>
          <h3 class="text-lg font-bold mb-2 text-[#ffd700]">Gold</h3>
        </template>
        <p v-if="levelData?.levels?.[3]?.reductions?.length">
          {{ levelData.levels[3].reductions.length }} items retrieved for Level 3.
        </p>
        <p v-else>No data found for Gold level.</p>
        <NuxtLink :to="{ name: 'worlds-id-levels-level_id', params: { id:sdgId , level_id: 3 }}">
          <p>Play</p>
        </NuxtLink>
      </UCard>
      <UButton label="Back to Worlds Overview" @click="goBack" />
    </div>
    </div>
    <div class="col-span-2">
      <LeaderBoard></LeaderBoard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useAsyncData } from "#app";
import { useRuntimeConfig } from "nuxt/app";
import { SDGGoal } from "~/types/sdg/goals";
import { useDimensionalityReductionsStore } from '~/stores/dimensionalityReductions';
import LeaderBoard from "~/components/LeaderBoard.vue";

const route = useRoute();
const router = useRouter();
const config = useRuntimeConfig();

const sdgId = parseInt(route.params.id as string, 10);

const dimensionalityReductionsStore = useDimensionalityReductionsStore();

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
// Fetch data on mount
onMounted(() => {
  dimensionalityReductionsStore.fetchReductions(sdgId);
});

// Computed properties for easier access
const levelData = computed(() => dimensionalityReductionsStore.reductions[sdgId] || {});
const levelFetching = computed(() => dimensionalityReductionsStore.fetching);
const levelError = computed(() => dimensionalityReductionsStore.error);

definePageMeta({
  layout: 'user'
})

// Fetch data on mount
onMounted(() => {
  dimensionalityReductionsStore.fetchReductions(sdgId);
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
