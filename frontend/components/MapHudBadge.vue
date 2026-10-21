<template>
  <!-- Small HUD status chip in the header of a map: which map is shown and whether data is syncing -->
  <span class="inline-flex items-center gap-2 rounded-full border border-line bg-surface-2/80 px-2.5 py-0.5 font-mono text-[11px] text-fg-dim">
    <span
      class="h-1.5 w-1.5 rounded-full"
      :class="busy ? 'animate-pulse bg-hero-amber' : 'bg-accent'"
      :style="!busy && color ? { background: color, boxShadow: `0 0 8px ${color}` } : {}"
    />
    {{ busy ? 'syncing…' : label }}
  </span>
</template>

<script setup lang="ts">
defineProps({
  label: { type: String, required: true },
  busy: { type: Boolean, default: false },
  color: { type: String, default: undefined },
});
</script>
