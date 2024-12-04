<template>
  <div>
    <!-- Left Pane: SDG Selection Menu -->
    <div>
      <!-- Display loading indicator -->
      <div v-if="loading" class="text-center">
        <span class="spinner"></span> Loading SDG Goals...
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

    <div class="card-container">
      <UCard
        v-for="goal in options"
        :key="goal.id"
        :class="{ 'selected-card': selected?.id === goal.id }"
        @click="selectGoal(goal)"
        class="sdg-card"
      >
        <template #header>
          <span class="text-center font-bold">Goal</span>
        </template>

        <img
          v-if="goal.icon"
          :src="`data:image/svg+xml;base64,${goal.icon}`"
          alt="SDG Icon"
          class="sdg-icon"
        />

        <template #footer>
          <span class="truncate text-sm text-center">{{ goal.id }}</span>
        </template>
      </UCard>
    </div>
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
.split-container {
  display: flex;
  width: 100%;
  gap: 20px;
}

.left-pane {
  flex: 1;
}

.right-pane {
  flex: 1;
  overflow-x: auto;
}

.card-container {
  display: flex;
  gap: 10px;
  flex-wrap: nowrap;
  align-items: center;
}

.sdg-card {
  width: 100px;
  border: 2px solid transparent;
  cursor: pointer;
  text-align: center;
}

.sdg-card:hover {
  border-color: #ccc;
}

.selected-card {
  border-color: black;
}

.sdg-icon {
  width: 64px;
  height: 64px;
  object-fit: contain;
  margin: 0 auto;
}

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
