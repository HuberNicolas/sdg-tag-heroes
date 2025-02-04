<template>
  <!-- Input field for the marked text -->
  <div class="container mx-auto p-4">
    <h3 class="font-semibold mb-2">Your Comment</h3>
    <textarea
      v-model="comment"
      class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
      rows="4"
      placeholder="Add your comment here..."
    ></textarea>
  </div>
</template>

<script setup lang="ts">
import { watch, ref } from "vue";
import { useExplanationsStore } from "~/stores/explanations";

const explanationStore = useExplanationsStore();
const comment = ref<string>(explanationStore.comment); // Initialize comment from the store

// Watch for changes to comment and update the store automatically
watch(comment, (newComment) => {
  explanationStore.setComment(newComment);
});
</script>
