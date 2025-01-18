<template>
  <div class="flex flex-row h-full">
    <div class="basis-1/2 h-full bg-red-400 relative">
      <p>SDG-Centered</p>
      <HexGlyph :values=values :height="600" :width="600" />

    </div>
    <div class="basis-1/2 h-full bg-blue-400">
      <p>Publication Centered</p>
    </div>
  </div>
</template>

<script setup lang="ts">

import HexGlyph from "~/components/GlyphOverview.vue";

const values = [0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6];
</script>

<style scoped>

</style>
