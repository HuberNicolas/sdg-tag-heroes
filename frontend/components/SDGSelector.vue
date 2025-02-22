<template>
  <div class="frame-container">
    <div class="frame-title"><b>Select</b> the SDG you want to see the machine explanation</div>
    <div>
      <!-- SDG Cards -->
      <div class="flex flex-wrap gap-1 p-1">
        <div
          v-for="sdg in sdgs"
          :key="sdg.id"
          @click="selectSDG(sdg.id)"
          :class="[
          'cursor-pointer flex flex-col items-center justify-center rounded-lg p-2 w-12 h-12 transition-all duration-200',
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
            class="w-10 h-10 object-contain"
          />
          <!-- SDG Short Title -->
          <span class="text-xs text-center mt-1">
          {{ sdg.shortTitle }}
        </span>
        </div>
      </div>
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
