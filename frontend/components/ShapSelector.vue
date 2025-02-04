<template>
  <div class="container mx-auto p-4">
    <!-- Display the marked text -->
    <div v-if="markedText" class="p-4 bg-gray-100 rounded-lg">
      <h3 class="font-semibold mb-2">Selected Abstract Section</h3>
      <p class="text-gray-700">{{ markedText }}</p>
    </div>
    <div v-else class="p-4 bg-gray-100 rounded-lg">
      <h3 class="font-semibold mb-2">Mark a section from the abstract to share your thoughts</h3>
      <p class="text-gray-500">No passage selected yet.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useExplanationsStore } from "~/stores/explanations";

const explanationStore = useExplanationsStore();
const markedText = computed(() => explanationStore.markedText); // Get marked text from the store

</script>
