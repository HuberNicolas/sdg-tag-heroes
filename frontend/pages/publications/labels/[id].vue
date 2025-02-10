<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Header -->
    <h1 class="text-2xl font-bold text-gray-800 mb-6">
      SDG Label Summary for Publication ID: {{ $route.params.id }}
    </h1>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-6">
      <p class="text-gray-500">Loading SDG data...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-50 p-4 rounded-md text-red-600 text-center">
      <p>{{ error }}</p>
    </div>

    <!-- Display SDG Label Summary -->


    <div v-if="sdgLabelSummary" class="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md">

      <!--
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
     -->

      <h2 class="text-xl font-semibold text-gray-800 mt-8 mb-4">SDG Labels:</h2>
      <!-- SDG Goals Grid -->
      <div v-if="!isLoading && sdgs.length" class="grid grid-cols-4 gap-4">
        <div
          v-for="sdg in sdgs"
          :key="sdg.id"
          class="flex flex-col items-center justify-center border rounded-lg p-4 shadow-md transition-opacity"
          :class="{
            'opacity-100': sdg.label === 1,
            'bg-gray-200': sdg.label === 0,
            'bg-red-200 opacity-80': sdg.label === -1,
          }"
          :style="sdg.label === 1 ? { backgroundColor: sdg.color } : {}"
        >
          <!-- SDG Icon -->
          <img
            v-if="sdg.icon && sdg.label === 1"
            :src="`data:image/svg+xml;base64,${sdg.icon}`"
            :alt="`SDG ${sdg.id} Icon`"
            class="w-8 h-8 object-contain"
          />
          <!-- Placeholder for Not Defined -->
          <div
            v-else-if="sdg.label === 0"
            class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center"
          >
            <span class="text-sm text-gray-800">?</span>
          </div>
          <!-- Placeholder for Definitely Not Related -->
          <div
            v-else-if="sdg.label === -1"
            class="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center"
          >
            <span class="text-sm text-white">X</span>
          </div>

          <!-- SDG Title -->
          <p
            class="mt-2 text-center font-semibold"
            :class="sdg.label === 1 ? 'text-white' : 'text-gray-600'"
          >
            SDG {{ sdg.id }}
          </p>
        </div>
      </div>
    </div>

    <!-- No Data State -->
    <div v-if="!isLoading && !sdgs.length && !error" class="text-center text-gray-600">
      <p>No SDG data available.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useSDGLabelSummariesStore } from '~/stores/sdgLabelSummaries';
import { useSDGsStore } from '~/stores/sdgs';

const route = useRoute();
const sdgLabelSummariesStore = useSDGLabelSummariesStore();
const sdgsStore = useSDGsStore();

// Fetch SDG Label Summary and SDGs on component mount
onMounted(async () => {
  const publicationId = Number(route.params.id);
  if (!isNaN(publicationId)) {
    await sdgLabelSummariesStore.fetchSDGLabelSummaryByPublicationId(publicationId);
  }
  if (!sdgsStore.sdgs.length) {
    await sdgsStore.fetchSDGs();
  }
});

// Computed properties for reactive data
const isLoading = computed(() => sdgLabelSummariesStore.isLoading || sdgsStore.isLoading);
const error = computed(() => sdgLabelSummariesStore.error || sdgsStore.error);
const sdgLabelSummary = computed(() => sdgLabelSummariesStore.sdgLabelSummaryForPublication);

const sdgs = computed(() => {
  if (!sdgLabelSummary.value || !sdgsStore.sdgs.length) return [];

  // Map SDGs and determine their label state
  return sdgsStore.sdgs.map((sdg, index) => {
    const sdgKey = `sdg${sdg.id}`; // Match SDG key (e.g., sdg1, sdg2)
    return {
      ...sdg,
      label: sdgLabelSummary.value[sdgKey], // 1, 0, or -1
    };
  });
});
</script>
