<template>
  <div class="h-screen flex flex-col">
    <h1 class="text-center text-2xl font-bold mb-4">Sustainable Development Goals</h1>

    <div v-if="error" class="text-red-500 text-center">Error: {{ error.message }}</div>
    <div v-else-if="pending" class="text-center">Loading...</div>

    <div
      v-else
      class="grid gap-2 flex-1"
      :style="gridStyle"
    >
      <!-- First 16 Goals -->
      <UCard
        v-for="goal in goals.slice(0, 16)"
        :key="goal.id"
        class="flex flex-col items-center justify-between text-center shadow-lg rounded-lg overflow-hidden"
        :style="{
          border: `4px solid ${goal.color}`,
          fontSize: fontSize,
          height: cardHeight,
        }"
      >
        <template #header>
          <h2 class="font-bold mb-1" :style="{ color: goal.color }">{{ goal.name }} - {{goal.id}}</h2>
        </template>
        <NuxtLink :to="{ name: 'worlds-id', params: { id: goal.id } }">
          <div class="flex items-center justify-center w-full h-[10%]">
            <img
              v-if="goal.icon"
              :src="`data:image/svg+xml;base64,${goal.icon}`"
              :alt="goal.name"
              class="w-[200%] h-[200%] object-contain"
            />
          </div>
        </NuxtLink>
        <template #footer>
          <p>Goal {{ goal.index }}</p>
        </template>
      </UCard>

      <!-- 17th Goal -->
      <div class="col-span-full flex justify-center">
        <UCard
          v-if="goals[16]"
          class="flex flex-col items-center justify-between text-center shadow-lg rounded-lg overflow-hidden"
          :style="{
            border: `4px solid ${goals[16].color}`,
            fontSize: fontSize,
            height: cardHeight,
          }"
        >
          <template #header>
            <h2 class="font-bold mb-1" :style="{ color: goals[16].color }">{{ goals[16].name }}</h2>
          </template>
          <NuxtLink :to="{ name: 'worlds-id', params: { id: goals[16].id } }">
            <div class="flex items-center justify-center w-full h-[10%]">
              <img
                v-if="goals[16].icon"
                :src="`data:image/svg+xml;base64,${goals[16].icon}`"
                :alt="goals[16].name"
                class="w-[200%] h-[200%] object-contain"
              />
            </div>
          </NuxtLink>
          <template #footer>
            <p>Goal {{ goals[16].index }}</p>
          </template>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
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

// Dynamically calculate the grid style to fit 17 elements on screen
const gridStyle = computed(() => {
  const columns = 4; // Number of columns
  const rows = Math.ceil(17 / columns); // Calculate rows based on 17 items
  return {
    gridTemplateColumns: `repeat(${columns}, 1fr)`,
    gridTemplateRows: `repeat(${rows}, 1fr)`,
  };
});

// Adjust font size and card height to scale with the viewport
const fontSize = "0.8rem"; // Adjust based on preference
const cardHeight = "calc((100vh - 4rem) / 5)"; // Dynamically calculate height to fit screen

definePageMeta({
  layout: 'empty'
})
</script>

<style scoped>
html,
body {
  margin: 0;
  padding: 0;
  overflow: hidden; /* Prevent scrolling */
}

.grid {
  display: grid;
  gap: 0.5rem;
}

img {
  object-fit: contain;
  margin: auto;
}

.col-span-full {
  grid-column: span 4; /* Ensure 17th card spans all columns */
}
</style>
