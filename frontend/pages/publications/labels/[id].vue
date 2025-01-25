<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Debugging: Log current state -->
    <div class="hidden">
      <p>isLoading: {{ isLoading }}</p>
      <p>error: {{ error }}</p>
      <p>sdgLabelSummary: {{ sdgLabelSummary }}</p>
    </div>

    <!-- Loading State with Skeleton -->
    <div v-if="isLoading" class="max-w-2xl mx-auto space-y-6">
      <div class="animate-pulse">
        <div class="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div class="space-y-4">
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
          <div class="h-4 bg-gray-200 rounded w-2/3"></div>
          <div class="h-4 bg-gray-200 rounded w-3/5"></div>
          <div class="h-4 bg-gray-200 rounded w-4/5"></div>
        </div>
        <div class="mt-6">
          <div class="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div class="grid grid-cols-2 gap-4">
            <div v-for="i in 17" :key="i" class="h-10 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="max-w-2xl mx-auto bg-red-50 p-4 rounded-md text-red-600 text-center">
      <p>{{ error }}</p>
    </div>

    <!-- Display SDG Label Summary -->
    <div v-if="sdgLabelSummary" class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
      <h1 class="text-2xl font-bold text-gray-800 mb-6">
        SDG Label Summary for Publication ID: {{ $route.params.id }}
      </h1>
      <div class="space-y-4">
        <div class="flex items-center space-x-2">
          <strong class="text-gray-700 w-32">Summary ID:</strong>
          <span class="text-gray-900">{{ sdgLabelSummary.sdgLabelSummaryId }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <strong class="text-gray-700 w-32">Publication ID:</strong>
          <span class="text-gray-900">{{ sdgLabelSummary.publicationId }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <strong class="text-gray-700 w-32">History ID:</strong>
          <span class="text-gray-900">{{ sdgLabelSummary.historyId }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <strong class="text-gray-700 w-32">Created At:</strong>
          <span class="text-gray-900">{{ sdgLabelSummary.createdAt }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <strong class="text-gray-700 w-32">Updated At:</strong>
          <span class="text-gray-900">{{ sdgLabelSummary.updatedAt }}</span>
        </div>
      </div>

      <h2 class="text-xl font-semibold text-gray-800 mt-8 mb-4">SDG Scores:</h2>
      <ul class="grid grid-cols-2 gap-4">
        <li
          v-for="(score, index) in sdgScores"
          :key="index"
          class="bg-gray-50 p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="flex items-center space-x-2">
            <strong class="text-gray-700">SDG {{ index + 1 }}:</strong>
            <span class="text-gray-900">{{ score }}</span>
          </div>
        </li>
      </ul>
    </div>

    <!-- No Data State -->
    <div v-if="!isLoading && !sdgLabelSummary && !error" class="max-w-2xl mx-auto text-center text-gray-600">
      <p>No SDG Label Summary found for this publication.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useSDGLabelSummariesStore } from '~/stores/sdgLabelSummaries';

const route = useRoute();
const sdgLabelSummariesStore = useSDGLabelSummariesStore();

// Fetch SDG Label Summary on component mount
onMounted(async () => {
  const publicationId = Number(route.params.id);
  if (!isNaN(publicationId)) {
    await sdgLabelSummariesStore.fetchSDGLabelSummaryByPublicationId(publicationId);
  }
});

// Computed properties
const isLoading = computed(() => sdgLabelSummariesStore.isLoading);
const error = computed(() => sdgLabelSummariesStore.error);
const sdgLabelSummary = computed(() => {
  console.log("SDG Label Summary in computed:", sdgLabelSummariesStore.sdgLabelSummaryForPublication);
  return sdgLabelSummariesStore.sdgLabelSummaryForPublication;
});


// Extract SDG scores dynamically
const sdgScores = computed(() => {
  if (!sdgLabelSummary.value) return [];
  return [
    sdgLabelSummary.value.sdg1,
    sdgLabelSummary.value.sdg2,
    sdgLabelSummary.value.sdg3,
    sdgLabelSummary.value.sdg4,
    sdgLabelSummary.value.sdg5,
    sdgLabelSummary.value.sdg6,
    sdgLabelSummary.value.sdg7,
    sdgLabelSummary.value.sdg8,
    sdgLabelSummary.value.sdg9,
    sdgLabelSummary.value.sdg10,
    sdgLabelSummary.value.sdg11,
    sdgLabelSummary.value.sdg12,
    sdgLabelSummary.value.sdg13,
    sdgLabelSummary.value.sdg14,
    sdgLabelSummary.value.sdg15,
    sdgLabelSummary.value.sdg16,
    sdgLabelSummary.value.sdg17,
  ];
});
</script>
