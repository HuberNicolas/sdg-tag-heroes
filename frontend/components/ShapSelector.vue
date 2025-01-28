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

    <!-- Input field for the marked text -->
    <div>
      <h3 class="font-semibold mb-2">Your Comment</h3>
      <textarea
        v-model="comment"
        class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        rows="4"
        placeholder="Add your comment here..."
      ></textarea>
    </div>

    <!-- SDG Selection -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Select SDG</label>
      <select
        v-model="selectedSDG"
        class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
      >
        <option v-for="sdg in sdgs" :key="sdg" :value="sdg">SDG {{ sdg }}</option>
      </select>
    </div>

    <UButton>Submit</UButton>

  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useExplanationsStore } from "~/stores/explanations";

const explanationStore = useExplanationsStore();
const markedText = computed(() => explanationStore.markedText); // Get marked text from the store
const comment = ref<string>("");
</script>
