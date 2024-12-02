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
      </div>
      <UButton label="Back to Worlds" @click="goBack" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useAsyncData } from "#app";
import { useRuntimeConfig } from "nuxt/app";
import { SDGGoal } from "~/types/sdg/goals";

const route = useRoute();
const router = useRouter();
const config = useRuntimeConfig();


const { data, pending, error } = await useAsyncData<SDGGoal>(
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

const goal = data?.value || null;

// Go back to the worlds overview
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
</style>
