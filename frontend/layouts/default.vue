<template>
  <div class="flex flex-col h-screen">
    <!-- Shared Navbar -->

    <!-- <p class="bg-gray-200 p-4 flex-none">Some default layout content shared across all pages</p> -->
    <p class="bg-gray-200 p-4 flex-none">Some default layout content shared across all pages</p>
    <!--<NavigationBar></NavigationBar> -->


    <!-- Slot Content -->
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
