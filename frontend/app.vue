<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <UNotifications />
</template>


<style>
.frame-container {
  @apply border border-gray-300 rounded-lg p-2 shadow-sm bg-gray-50;
  /* display: contents; /* Ensures the container doesn't interfere with the grid */
}

.frame-title {
  @apply text-gray-700 font-normal text-sm mb-1;
}
</style>
