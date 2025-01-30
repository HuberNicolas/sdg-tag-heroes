<template>
  <UTooltip :text="tooltip">
    <UChip size="md" position="bottom-right" :ui="{ base: '-mx-2 rounded-none ring-0', background: '' }">
      <template #content>
        <UAvatar :icon="icon" size="xl" />
      </template>
    </UChip>
  </UTooltip>
</template>

<script setup lang="ts">
defineProps({
  icon: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  tooltip: {
    type: String,
    required: false
  }
});
</script>
