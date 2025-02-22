<template>
  <div class="max-w-4xl mx-auto p-2">
    <h2 class="text-xl font-semibold text-center text-gray-700 mb-1">
      Community Label Summary
    </h2>

    <div v-if="isLoading" class="text-gray-500 text-center">
      Summarizing Community Label Reasons
    </div>

    <div v-if="error" class="max-h-[100px] bg-gray-100 p-2 rounded-md overflow-y-auto text-center">
      No Comments Available
    </div>

    <div v-if="commentSummary" class="max-h-[100px] bg-gray-100 p-2 rounded-md overflow-y-auto">
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
