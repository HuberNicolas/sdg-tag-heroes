<template>
  <div>
    <!-- SDG Cards -->
    <div class="flex flex-wrap gap-1 p-1">
      <div
        v-for="sdg in sdgs"
        :key="sdg.id"
        @click="selectSDG(sdg.id)"
        :class="[
          'cursor-pointer flex flex-col items-center justify-center border-2 rounded-lg p-1 w-18 h-18',
          selectedSDG === sdg.id ? 'border-black bg-gray-100' : 'border-gray-200 hover:border-gray-400',
        ]"
      >
        <!-- SDG Icon -->
        <img
          v-if="sdg.icon"
          :src="`data:image/svg+xml;base64,${sdg.icon}`"
          :alt="`SDG ${sdg.id} Icon`"
          class="w-6 h-6 object-contain"
        />

        <!-- SDG Short Title -->
        <span class="text-xs text-center text-gray-700 mt-1">
          {{ sdg.shortTitle }}
        </span>
      </div>

      <!-- Reset Button -->
      <button
        @click="resetSelection"
        class="mb-1 px-1 py-1 text-sm text-white bg-red-500 rounded hover:bg-red-600 transition-colors"
      >
        Reset
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import { baseSdgShortTitles } from "~/constants/sdgs";

const sdgsStore = useSDGsStore();
const selectedSDG = computed(() => sdgsStore.getSelectedSDG);

// Fetch SDGs on mount
onMounted(async () => {
  if (!sdgsStore.sdgs.length) {
    await sdgsStore.fetchSDGs();
  }
});

const sdgs = computed(() =>
  sdgsStore.sdgs.map((sdg, index) => ({
    id: sdg.id,
    color: sdg.color,
    shortTitle: baseSdgShortTitles[index],
    icon: sdg.icon,
  }))
);

const selectSDG = (sdgId: number) => {
  if (selectedSDG.value === sdgId) {
    // Deselect if already selected
    sdgsStore.setSelectedSDG(0); // Assuming 0 means no selection
  } else {
    // Select the SDG
    sdgsStore.setSelectedSDG(sdgId);
  }
};

const resetSelection = () => {
  sdgsStore.setSelectedSDG(0); // Reset to no selection
};
</script>
