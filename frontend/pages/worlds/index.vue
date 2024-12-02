<template>
  <div>
    <h1 class="text-center text-2xl font-bold mb-6">Sustainable Development Goals</h1>

    <div v-if="error" class="text-red-500 text-center">Error: {{ error.message }}</div>
    <div v-else-if="pending" class="text-center">Loading...</div>

    <div
      v-else
      class="grid grid-cols-4 gap-6 px-4 auto-rows-fr"
      :style="{ gridTemplateRows: 'repeat(4, 1fr)' }"
    >

        <UCard
          v-for="goal in goals.slice(0, 16)"
          :key="goal.id"
          class="aspect-square flex flex-col items-center justify-between text-center shadow-lg rounded-lg overflow-hidden"
          :style="{ border: `4px solid ${goal.color}` }"
        >

          <template #header>
            <h2 class="text-lg font-bold mb-2" :style="{ color: goal.color }">{{ goal.name }}</h2>
          </template>
          <NuxtLink :to="{name: 'worlds-id', params: {id: goal.id}}">
          <img
            v-if="goal.icon"
            :src="`data:image/svg+xml;base64,${goal.icon}`"
            :alt="goal.name"
            class="w-full h-full object-contain"
          />
          </NuxtLink>
          <template #footer>
            <p class="text-sm mt-4">Goal {{ goal.index }}</p>
          </template>

        </UCard>


      <!-- 17th Goal in the Middle -->
      <div class="col-span-8 flex justify-center">
        <UCard
          v-if="goals[16]"
          class="aspect-square flex flex-col items-center justify-between text-center shadow-lg rounded-lg overflow-hidden w-1/2"
          :style="{ border: `4px solid ${goals[16].color}` }"
        >

            <template #header>
              <h2 class="text-lg font-bold mb-2" :style="{ color: goals[16].color }">{{ goals[16].name }}</h2>
            </template>
          <NuxtLink :to="{name: 'worlds-id', params: {id: goals[16].id}}">
            <img
              v-if="goals[16].icon"
              :src="`data:image/svg+xml;base64,${goals[16].icon}`"
              :alt="goals[16].name"
              class="w-full h-full object-contain"
            />
          </NuxtLink>
            <template #footer>
              <p class="text-sm mt-4">Goal {{ goals[16].index }}</p>
            </template>

        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRuntimeConfig } from "nuxt/app";
import { SDGGoal } from "~/types/sdg/goals";

const config = useRuntimeConfig();

// Fetch SDG goals
const { data, pending, error } = await useAsyncData<SDGGoal[]>("sdgGoals", async () => {
  const response = await $fetch<{ items: SDGGoal[] }>(`${config.public.apiUrl}sdgs`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
  });
  return response.items;
});

const goals = data?.value || [];
</script>

<style scoped>
.grid {
  display: grid;
  gap: 0.5rem;
}

.auto-rows-fr {
  grid-auto-rows: 1fr;
}

img {
  object-fit: contain;
  margin: auto;
}

h2 {
  margin-bottom: 1rem;
}

.col-span-8 {
  grid-column: span 8;
}
</style>
