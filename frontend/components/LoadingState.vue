<template>
  <!-- Loading indicator: a small honeycomb whose cells light up one after another -->
  <div
    class="loading-state"
    :class="[`loading-state--${size}`, { 'loading-state--overlay': overlay }]"
    role="status"
    aria-live="polite"
  >
    <svg class="loading-state__comb" viewBox="-34 -30 68 60" aria-hidden="true">
      <polygon
        v-for="(cell, i) in cells"
        :key="i"
        :points="cell"
        class="loading-state__cell"
        :style="{ animationDelay: `${i * 110}ms`, fill: colors[i] }"
      />
    </svg>
    <span v-if="label" class="loading-state__label">
      {{ label }}<span class="animate-blink">_</span>
    </span>
  </div>
</template>

<script setup lang="ts">
import { baseSdgColors } from "@/constants/constants";

defineProps({
  label: { type: String, default: "loading" },
  size: { type: String as PropType<"sm" | "md">, default: "md" },
  // Cover the parent (which needs `relative`) with a blurred layer
  overlay: { type: Boolean, default: false },
});

// Centre cell and its six neighbours (flat-top hexagons, radius 9)
const r = 9;
const hex = (cx: number, cy: number) =>
  Array.from({ length: 6 }, (_, k) => {
    const a = (Math.PI / 3) * k;
    return `${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`;
  }).join(" ");
const dx = r * 1.5 + 1;
const dy = (Math.sqrt(3) / 2) * r + 0.6;
const centres: [number, number][] = [
  [0, 0], [0, -2 * dy], [dx, -dy], [dx, dy], [0, 2 * dy], [-dx, dy], [-dx, -dy],
];
const cells = centres.map(([x, y]) => hex(x, y));
const colors = [0, 12, 5, 6, 2, 13, 4].map((i) => baseSdgColors[i]);
</script>

<style scoped>
.loading-state {
  @apply flex flex-col items-center justify-center gap-3 p-4 text-center;
}
.loading-state--sm {
  @apply flex-row gap-2 p-2;
}
.loading-state--overlay {
  @apply absolute inset-0 z-10 rounded-[inherit] bg-surface/70 backdrop-blur-[2px];
}
.loading-state__comb {
  @apply h-12 w-12;
}
.loading-state--sm .loading-state__comb {
  @apply h-6 w-6;
}
.loading-state__cell {
  opacity: 0.18;
  animation: cell-pulse 1.4s ease-in-out infinite;
}
.loading-state__label {
  @apply font-mono text-xs text-fg-dim;
}

@keyframes cell-pulse {
  0%,
  100% {
    opacity: 0.18;
  }
  35% {
    opacity: 1;
  }
}
</style>
