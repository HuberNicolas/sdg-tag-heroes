<template>
  <!-- Input field for the marked text -->
  <div class="container mx-auto p-2">
    <h3 class="font-semibold mb-0.5">Your Comment</h3>
    <textarea
      v-model="comment"
      class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-gray-500 focus:border-gray-500"
      rows="1"
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
