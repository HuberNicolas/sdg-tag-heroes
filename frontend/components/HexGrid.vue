<template>
  <div ref="hexGridContainer" class="hex-grid">
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import useHexGrid from '@/composables/useHexGrid';

const values = [0.8, 0.9, 0.7, 0.5, 0.6, 0.4, 0.3, 0.9, 1.0, 0.7, 0.6, 0.4, 0.5, 0.8, 0.6, 0.4, 0.7];

const hexGridContainer = ref<HTMLDivElement | null>(null);
let isRendered = false; // Flag to ensure `renderHexGrid` is called only once

onMounted(() => {
  if (!isRendered && hexGridContainer.value) {
    const { renderHexGrid } = useHexGrid(values);
    renderHexGrid(hexGridContainer.value);
    isRendered = true; // Mark as rendered
  }
});

// Optional cleanup if needed
onUnmounted(() => {
  if (hexGridContainer.value) {
    hexGridContainer.value.innerHTML = ''; // Clear the container
  }
});
</script>

<style scoped>
.hex-grid {
  width: 100%;
  height: 100%;
}
</style>
