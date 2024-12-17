<template>
  <div>

    <!-- Flexbox layout to display all SDG Cards in one row -->
    <div class="flex flex-nowrap gap-2 overflow-x-auto p-2">
      <!-- SDG Icons -->
      <div
        v-for="goal in options"
        :key="goal.id"
        @click="selectGoal(goal)"
        :class="[
      'cursor-pointer flex flex-col items-center justify-center border-2 rounded-lg p-2',
      selected?.id === goal.id ? 'border-black' : 'border-gray-200 hover:border-gray-400',
    ]"
        class="w-16 h-20 shrink-0"
      >
        <!-- SDG Goal ID -->
        <span class="text-xs font-medium text-gray-600 mb-1">
      Goal {{ goal.id }}
    </span>

        <!-- SDG Icon -->
        <img
          v-if="goal.icon"
          :src="`data:image/svg+xml;base64,${goal.icon}`"
          :alt="`SDG ${goal.id} Icon`"
          class="w-12 h-12 object-contain"
        />
      </div>
    </div>
    <!-- Display loading indicator -->
    <div v-if="loading" class="text-center">
      <span class="spinner animate-spin"></span> Loading SDG Goals...
    </div>

    <!-- Display error message -->
    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <!-- Display fallback if no SDG goals are available -->
    <div v-else-if="options.length === 0" class="text-gray-500">
      No SDG Goals available.
    </div>

    <!-- SDG Selection Menu -->
    <UInputMenu
      v-else
      v-model="selected"
      :options="options"
      placeholder="Select an SDG Goal"
      by="id"
      option-attribute="name"
      :search-attributes="['name']"
    >
      <template #option="{ option: goal }">
        <span class="truncate">{{ goal.id }} - {{ goal.name }}</span>
      </template>
    </UInputMenu>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watchEffect } from 'vue';
import { useSDGStore } from '@/stores/sdgs';

const sdgStore = useSDGStore();
const selected = ref(null);

// Fetch SDG goals on mount
onMounted(async () => {
  if (!sdgStore.goals.length) {
    await sdgStore.fetchSDGGoals();
  }
});

// Reactive computed options for the dropdown and cards
const options = computed(() =>
  Array.isArray(sdgStore.goals.items)
    ? sdgStore.goals.items.map(goal => ({
      id: goal.id,
      name: goal.name,
      icon: goal.icon,
    }))
    : []
);

const loading = computed(() => sdgStore.loading);
const error = computed(() => sdgStore.error);

// Sync dropdown with card selection
watchEffect(() => {
  if (selected.value) {
    sdgStore.selectedGoal = selected.value.id;
  }
});

// Function to handle card click
const selectGoal = goal => {
  selected.value = goal; // Sync with dropdown
};
</script>

<style scoped>

.spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}
</style>
