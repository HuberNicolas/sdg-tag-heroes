<template>
  <div>
    <!-- SDG Card -->
    <div
      v-if="currentSDG"
      class="flex flex-col items-center p-4 border rounded-lg shadow-lg bg-white"
    >
      <!-- SDG Icon and Short Title -->
      <img
        :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
        :alt="`SDG ${currentSDG.id} Icon`"
        class="w-16 h-16"
      />
      <p class="text-sm text-gray-600">{{ currentSDG.index }}</p>
      <p class="text-sm text-gray-600">{{ currentSDG.shortTitle }}</p>
    </div>
    <div v-else class="text-gray-600">No SDG Selected</div>
  </div>
</template>
<script setup lang="ts">
import { computed } from "vue";
import { useSDGsStore } from "~/stores/sdgs";

const sdgsStore = useSDGsStore();

// Get the selected SDG from the store
const currentSDG = computed(() => {
  const sdgId = sdgsStore.getSelectedSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});
</script>
