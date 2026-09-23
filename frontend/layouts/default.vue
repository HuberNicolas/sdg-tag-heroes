<template>
  <div class="flex flex-col h-dvh overflow-hidden bg-white">
    <NavigationBar class="flex-none" />
    <!-- Pages fill the remaining height; on small screens they scroll instead of being cut off.
         On ultrawide screens the content is capped and centred so panels do not stretch apart. -->
    <main class="flex-1 min-h-0 overflow-y-auto">
      <div class="h-full w-full max-w-[2560px] mx-auto">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import NavigationBar from "~/components/NavigationBar.vue";
</script>
