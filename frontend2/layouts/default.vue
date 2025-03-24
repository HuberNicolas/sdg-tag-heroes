<template>
  <div class="flex flex-col h-screen overflow-hidden">
    <NavigationBar class="h-16 flex-none" />
    <div class="flex-1 overflow-hidden">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import NavigationBar from "~/components/NavigationBar.vue";
</script>

<style scoped>
</style>
