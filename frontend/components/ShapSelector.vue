<template>
  <div class="container mx-auto p-4">
    <!-- Display the marked text -->
    <div v-if="firstLastWords" class="p-4 bg-gray-100 rounded-lg">
      <h3 class="font-semibold mb-2">Selected Abstract Section</h3>
      <p class="text-gray-700">{{ firstLastWords }}</p>
    </div>
    <div v-else class="p-4 bg-gray-100 rounded-lg">
      <h3 class="font-semibold mb-2">Selected Abstract Section</h3>
      <p class="text-gray-500">No passage selected yet.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useExplanationsStore } from "~/stores/explanations";

const explanationStore = useExplanationsStore();
const markedText = computed(() => explanationStore.markedText); // Get marked text from the store

// Extract the first and last words of the marked text
const firstLastWords = computed(() => {
  if (markedText.value) {
    const words = markedText.value.trim().split(/\s+/);
    if (words.length === 1) {
      return words[0]; // If there's only one word, display it
    } else if (words.length > 1) {
      return `${words[0]} ... ${words[words.length - 1]}`;
    }
  }
  return ''; // Return an empty string if no marked text is selected
});
</script>
