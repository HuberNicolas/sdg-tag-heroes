<template>
  <div class="flex items-center justify-start bg-white border rounded-lg shadow px-4 py-2 space-x-3">
    <template v-if="currentSDG">
      <!-- SDG Icon -->
      <img
        :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
        :alt="`SDG ${currentSDG.id} Icon`"
        class="w-8 h-8 flex-shrink-0"
      />

      <!-- SDG Details (Compact) -->
      <div class="flex items-center space-x-2">
        <p class="text-sm font-semibold text-gray-800">SDG {{ currentSDG.index }}</p>
        <p class="text-sm text-gray-600 truncate">{{ currentSDG.name }}</p>

        <p v-if="machineScore !== null" class="text-sm text-gray-600">
          (Machine Score: <span class="font-semibold">{{ machineScore.toFixed(2) }}</span>)
        </p>
      </div>
    </template>

    <template v-else>
      <!-- Placeholder (Compact) -->
      <div class="flex items-center space-x-2 text-gray-500">
        <Icon name="ph-hexagon-light" class="w-8 h-8" />
        <p class="text-sm truncate">Select an SDG to see machine explanation in the text below</p>
      </div>
    </template>
  </div>
</template>



<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";

const sdgsStore = useSDGsStore();
const sdgPredictionsStore = useSDGPredictionsStore();

// Get the selected SDG
const currentSDG = computed(() => {
  const sdgId = sdgsStore.getSelectedSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Compute the machine score based on the selected SDG
const machineScore = computed(() => {
  if (!currentSDG.value || !sdgPredictionsStore.labelingSDGPrediction) return null;

  // Extract the score dynamically from the prediction object
  return sdgPredictionsStore.labelingSDGPrediction[`sdg${currentSDG.value.id}`] ?? null;
});

// Fetch SDG Predictions when component mounts
onMounted(async () => {
  if (!sdgPredictionsStore.labelingSDGPrediction) {
    await sdgPredictionsStore.fetchDefaultModelSDGPredictionsByPublicationId(1); // Adjust `1` as needed
  }
});

</script>
