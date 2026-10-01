<template>
  <!-- Honeycomb of the community votes; click a cell to pick your label (composables/plots/connect.ts) -->
  <div id="glyph-container" class="w-full h-[15rem] 2xl:h-[17rem]" />
</template>

<script setup lang="ts">
import useConnect from '@/composables/plots/connect';

useConnect();
</script>
