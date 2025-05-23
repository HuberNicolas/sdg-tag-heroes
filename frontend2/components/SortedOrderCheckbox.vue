<template>
  <div class="flex items-center gap-2">
    <UCheckbox
      id="sortOrder"
      v-model="sortDescending"
      color="primary"
      size="sm"
    />
    <label for="sortOrder" class="text-sm font-medium">
      Sort by Most Votes
    </label>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed } from "vue";

const props = defineProps({
  modelValue: Boolean,
});

const emit = defineEmits(["update:modelValue"]);

const sortDescending = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});
</script>
