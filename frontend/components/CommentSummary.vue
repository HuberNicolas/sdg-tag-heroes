<template>
  <div class="max-w-4xl mx-auto p-4">
    <div v-if="isLoading" class="text-blue-500">Loading...</div>
    <div v-if="error" class="text-red-500">Error: {{ error }}</div>
    <div v-if="commentSummary" class="max-h-[100px] bg-gray-100 p-4 rounded-md overflow-y-auto">
      <p>{{ commentSummary.summary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";

const labelDecisionsStore = useLabelDecisionsStore();

const isLoading = computed(() => labelDecisionsStore.isLoading);
const error = computed(() => labelDecisionsStore.error);
const commentSummary = computed(() => labelDecisionsStore.commentSummary);
const userLabels = computed(() => labelDecisionsStore.userLabels);

// Watch for changes in userLabels and fetch comment summary
watch(userLabels, async (newUserLabels) => {
  const userLabelIds = newUserLabels.map(label => label.labelId);
  if (userLabelIds.length > 0) {
    await labelDecisionsStore.fetchCommentSummary(userLabelIds);
  }
}, { immediate: true });
</script>
