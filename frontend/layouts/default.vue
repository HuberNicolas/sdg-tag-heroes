<template>
  <div class="flex flex-col h-screen">
    <!-- Shared Navbar -->
    <p class="bg-gray-200 p-4 flex-none">Some default layout content shared across all pages</p>

    <!-- Slot Content -->
    <div class="flex-1 overflow-hidden">
      <slot />
    </div>
  </div>
</template>

<style scoped>
</style>
