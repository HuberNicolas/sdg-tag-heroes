<script setup lang="ts">
import { ref } from "vue";
import usePublications from "~/composables/usePublications";

const publications = ref<PublicationSchemaBase[]>([]);
const { getPublicationsByIds } = usePublications();

// Fetch publications by IDs
async function fetchPublications() {
  try {
    publications.value = await getPublicationsByIds([1, 2, 3]);
  } catch (error) {
    console.error(error);
  }
}

fetchPublications();
</script>

<template>
  <div>
    <h1>Publications</h1>
    <ul>
      <li v-for="pub in publications" :key="pub.publicationId">
        {{ pub.title }}
      </li>
    </ul>
  </div>
</template>
