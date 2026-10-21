<template>
  <!-- Thin bar under the navigation while API requests are running -->
  <div class="pointer-events-none relative h-0.5 w-full overflow-hidden" aria-hidden="true">
    <!-- CSS fade only, so the bar cannot get stuck in a hidden tab (Vue transitions wait for an animation frame) -->
    <div class="activity-bar absolute inset-0" :class="{ 'is-busy': isBusy }" />
  </div>
</template>

<script setup lang="ts">
const { isBusy } = useApiActivity();
</script>

<style scoped>
.activity-bar {
  background: linear-gradient(
    90deg,
    transparent,
    rgb(var(--c-accent)) 30%,
    rgb(var(--c-blue)) 60%,
    transparent
  );
  background-size: 50% 100%;
  background-repeat: no-repeat;
  animation: sweep 1.1s cubic-bezier(0.65, 0, 0.35, 1) infinite;
}
@keyframes sweep {
  from {
    background-position: -50% 0;
  }
  to {
    background-position: 150% 0;
  }
}
.activity-bar {
  opacity: 0;
  transition: opacity 0.3s;
  animation-play-state: paused;
}
.activity-bar.is-busy {
  opacity: 1;
  animation-play-state: running;
}
</style>
