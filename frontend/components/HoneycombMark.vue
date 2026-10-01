<template>
  <!-- Decorative honeycomb of the 17 SDGs, same layout as the SDG glyph of the game (constants/sdgs.ts) -->
  <svg
    :viewBox="viewBox"
    class="honeycomb"
    role="img"
    aria-label="Honeycomb of the 17 Sustainable Development Goals"
  >
    <g
      v-for="hex in hexes"
      :key="hex.index"
      class="honeycomb__cell"
      :style="{ animationDelay: `${hex.index * 45}ms` }"
    >
      <title>SDG {{ hex.index + 1 }}: {{ baseSdgTitles[hex.index] }}</title>
      <polygon :points="hex.points" :fill="hex.color" />
      <text
        v-if="labels"
        :x="hex.x"
        :y="hex.y"
        text-anchor="middle"
        dominant-baseline="central"
        class="honeycomb__label"
      >{{ hex.index + 1 }}</text>
    </g>
  </svg>
</template>

<script setup lang="ts">
import { baseCoords, baseSdgColors, baseSdgTitles } from "@/constants/constants";

defineProps({
  labels: { type: Boolean, default: true },
});

const r = 50;
const scale = 0.92;
const xSpacing = r * 2 * scale;
const ySpacing = Math.sqrt(3) * r * scale;

const hexes = baseCoords.map(([cx, cy], index) => {
  const x = cx * xSpacing;
  const y = cy * ySpacing;
  const points = Array.from({ length: 6 }, (_, k) => {
    const angle = (Math.PI / 3) * k + Math.PI / 6; // pointy-top, like the game's glyph
    return `${(x + r * Math.cos(angle)).toFixed(2)},${(y + r * Math.sin(angle)).toFixed(2)}`;
  }).join(" ");
  return { index, x, y, points, color: baseSdgColors[index] };
});

const xs = hexes.map((h) => h.x);
const ys = hexes.map((h) => h.y);
const pad = r + 4;
const viewBox = `${Math.min(...xs) - pad} ${Math.min(...ys) - pad} ${Math.max(...xs) - Math.min(...xs) + 2 * pad} ${
  Math.max(...ys) - Math.min(...ys) + 2 * pad
}`;
</script>

<style scoped>
.honeycomb {
  overflow: visible;
}
.honeycomb__cell {
  transform-box: fill-box;
  transform-origin: center;
  animation: cell-in 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), filter 0.25s;
}
.honeycomb__cell:hover {
  transform: scale(1.08);
  filter: drop-shadow(0 6px 14px rgb(0 0 0 / 0.35));
}
.honeycomb__cell polygon {
  stroke: rgb(var(--c-bg));
  stroke-width: 3;
}
.honeycomb__label {
  fill: #fff;
  font-family: var(--font-mono);
  font-size: 22px;
  font-weight: 600;
  pointer-events: none;
}

@keyframes cell-in {
  from {
    opacity: 0;
    transform: scale(0.4) rotate(-30deg);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
</style>
