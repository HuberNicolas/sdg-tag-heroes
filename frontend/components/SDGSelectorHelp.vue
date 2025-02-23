<template>
  <div class="frame-container">
    <div class="frame-title"><b>Select</b> an SDG to see details</div>

    <!-- SDG Cards -->
    <div class="flex flex-wrap gap-2 p-2">
      <div
        v-for="(sdg, index) in sdgs"
        :key="sdg.id"
        @click="toggleSDG(sdg.id)"
        :class="[
          'cursor-pointer flex flex-col items-center justify-center rounded-lg p-2 w-15 h-15 transition-all duration-200',
          selectedSDG === sdg.id
            ? 'bg-gray-300 border-2 border-black' // Selected state
            : 'bg-white hover:bg-gray-100 border-2 border-transparent hover:border-gray-200', // Default and hover states
        ]"
      >
        <!-- SDG Icon -->
        <img
          v-if="sdg.icon"
          :src="`data:image/svg+xml;base64,${sdg.icon}`"
          :alt="`SDG ${sdg.id} Icon`"
          class="w-14 h-14 object-contain"
        />
        <!-- SDG Short Title from baseSdgShortTitles -->
        <span class="text-xs text-center mt-1">
          {{ baseSdgShortTitles[index] }}
        </span>
      </div>
    </div>

    <!-- SDG Detailed Explanation -->
    <div v-if="selectedSDGDetails" class="mt-4 p-3 border rounded-lg bg-gray-50">
      <h3 class="text-sm font-semibold text-gray-700 flex items-center gap-2">
        SDG {{selectedSDGDetails.id}} - {{ selectedSDGDetails.name }}
      </h3>
      <p class="text-xs text-gray-600">
        {{ selectedSDGDetails.explanation }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import { baseSdgShortTitles } from "~/constants/sdgs";

const sdgsStore = useSDGsStore();
const selectedSDG = ref<number | null>(null);

// Fetch SDGs on mount
onMounted(async () => {
  if (!sdgsStore.sdgs.length) {
    await sdgsStore.fetchSDGs();
  }
});

// Get SDG list
const sdgs = computed(() => sdgsStore.sdgs);

// Get selected SDG details
const selectedSDGDetails = computed(() => sdgs.value.find(s => s.id === selectedSDG.value) || null);

const toggleSDG = (sdgId: number) => {
  selectedSDG.value = selectedSDG.value === sdgId ? null : sdgId;
};

const resetSelection = () => {
  selectedSDG.value = null;
};
</script>
