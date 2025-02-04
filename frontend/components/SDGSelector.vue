<template>
  <div>
    <!-- SDG Cards -->
    <div class="flex flex-wrap gap-1 p-1">
      <div
        v-for="sdg in sdgs"
        :key="sdg.id"
        @click="selectSDG(sdg.id)"
        :class="[
          'cursor-pointer flex flex-col items-center justify-center rounded-lg p-1 w-12 h-12',
          selectedSDG === sdg.id ? 'bg-base-200' : 'hover:bg-base-100',
        ]"
      >
        <!-- SDG Icon -->
        <img
          v-if="sdg.icon"
          :src="`data:image/svg+xml;base64,${sdg.icon}`"
          :alt="`SDG ${sdg.id} Icon`"
          class="w-8 h-8 object-contain"
        />

        <!-- SDG Short Title -->
        <span class="text-xs text-center text-gray-700 mt-1">
          {{ sdg.shortTitle }}
        </span>
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
