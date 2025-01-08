<template>
  <div>
    <ExplorationBar></ExplorationBar>
    <slot />
  </div>
</template>
<script setup lang="ts">
import ExplorationBar from "~/components/ExplorationBar.vue";
</script>
