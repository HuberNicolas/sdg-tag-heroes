<template>
  <div>
    <p>{{sdgId}}</p>
    <p>{{levelId}}</p>
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
const goBack = () => {
  router.push("/worlds");
};
</script>


<style scoped>

</style>
