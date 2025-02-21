<template>
  <div>
    <!-- SDG Card -->
    <div
      class="flex flex-col items-center p-2 border rounded-lg shadow-lg bg-white"
    >
      <template v-if="currentSDG">
        <!-- SDG Icon and Short Title -->
        <img
          :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
          :alt="`SDG ${currentSDG.id} Icon`"
          class="w-10 h-10"
        />
        <p class="text-sm text-gray-600">Goal No. {{ currentSDG.index }}</p>
        <p class="text-sm text-gray-600">{{ currentSDG.shortTitle }}</p>
      </template>

      <template v-else>
        <!-- Consistent Placeholder (Same Size) -->
        <Icon name="ph-hexagon-light" class="w-10 h-10 text-gray-400" />
        <p class="text-sm text-gray-600 text-center">
          Please select an SDG to see machine explanation
        </p>
      </template>
    </div>
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
