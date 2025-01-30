<template>
  <UTooltip :text="tooltip">
    <UButton
      size="md"
      shape="round"
      :ui="{ base: 'ring-0' }"
    >
      <template #default>
        <UAvatar :icon="icon" size="xl" />
      </template>
    </UButton>
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
