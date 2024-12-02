<template>
  <div>
    <p>{{sdgId}} - {{levelId}}</p>
    <UButton label="Back to Worlds Overview" @click="goBackToWorlds" />
    <UButton label="Back to World" @click="goBackToWorld" />
  </div>
</template>

<script setup lang="ts">
import { useRuntimeConfig } from "nuxt/app";

definePageMeta({
  middleware: ['level-guard'],
});

const route = useRoute();
const router = useRouter();
const config = useRuntimeConfig();

const sdgId = route.params.id;
const levelId = route.params.level_id;


// Navigate back
const goBackToWorlds = () => {
  router.push("/worlds");
};

const goBackToWorld = () => {
  // Use the current `id` parameter from the route
  const worldId = route.params.id;

  // Navigate back to `/worlds/:id`
  router.push({ name: 'worlds-id', params: { id: worldId } });
};
</script>


<style scoped>

</style>
