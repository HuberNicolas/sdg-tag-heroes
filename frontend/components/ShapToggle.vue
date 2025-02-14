<template>
  <div>
    <label class="inline-flex items-center">
      <input
        type="checkbox"
        v-model="showShap"
        class="form-checkbox h-5 w-5 text-blue-600"
      />
      <span class="ml-2 text-gray-700">Show Machine Explanation</span>
    </label>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useExplanationsStore } from '~/stores/explanations';

const explanationStore = useExplanationsStore();
const showShap = computed({
  get: () => explanationStore.showShap,
  set: (value) => explanationStore.setShowShap(value),
});
</script>
