<template>
  <!-- Quest marker in the publication table: small diamond plus name -->
  <span class="inline-flex items-center gap-1.5 whitespace-nowrap" :title="tooltip">
    <span class="quest-gem"><Icon :name="icon" /></span>
    <span class="font-mono text-[11px] text-fg-dim">{{ name }}</span>
  </span>
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
    required: false,
    default: undefined
  }
});
</script>
