<template>
  <!-- Legend of the publication map, one entry per visual channel (shape, size, colour, markers) -->
  <div class="map-legend" role="list" aria-label="Map legend">
    <div class="map-legend__group" role="listitem">
      <span class="map-legend__key">shape</span>
      <span class="map-legend__item" title="A publication">
        <svg viewBox="-12 -12 24 24"><polygon :points="hex(9)" class="lg-mark" /></svg>publication
      </span>
      <span class="map-legend__item" title="A quest publication: the community needs help with its label">
        <svg viewBox="-12 -12 24 24"><polygon :points="diamond(9)" class="lg-mark lg-mark--quest" /></svg>quest
      </span>
    </div>

    <div class="map-legend__group" role="listitem">
      <span class="map-legend__key">size</span>
      <span class="map-legend__item" title="Bigger cells give more XP (the machine is less certain about them)">
        <svg viewBox="-34 -12 68 24">
          <polygon :points="hex(4, -24)" class="lg-mark" />
          <polygon :points="hex(7, -9)" class="lg-mark" />
          <polygon :points="hex(10.5, 13)" class="lg-mark" />
        </svg>
        xp low → high
      </span>
    </div>

    <div v-if="variant === 'publications'" class="map-legend__group" role="listitem">
      <span class="map-legend__key">colour</span>
      <span class="map-legend__item" title="Fill: the SDG with the highest machine score">
        <span class="map-legend__sdgs">
          <span
            v-for="(c, i) in baseSdgColors"
            :key="i"
            class="hex-clip"
            :style="{ background: c }"
            :title="`SDG ${i + 1}: ${baseSdgTitles[i]}`"
          />
        </span>
        top SDG (machine)
      </span>
    </div>

    <div v-else class="map-legend__group" role="listitem">
      <span class="map-legend__key">colour</span>
      <span class="map-legend__item" title="Fill: the SDG world you are in. Outline: the SDG with the highest machine score, here the same">
        <svg viewBox="-12 -12 24 24"><polygon :points="hex(8)" :style="{ fill: sdgColor, stroke: sdgColor }" class="lg-ring" /></svg>
        top SDG = world
      </span>
      <span class="map-legend__item" title="Fill: the SDG world you are in. Outline: the SDG with the highest machine score, here another SDG">
        <svg viewBox="-12 -12 24 24"><polygon :points="hex(8)" :style="{ fill: sdgColor, stroke: otherColor }" class="lg-ring" /></svg>
        top SDG ≠ world
      </span>
    </div>

    <div class="map-legend__group" role="listitem">
      <span class="map-legend__key">markers</span>
      <span class="map-legend__item" title="Your point of interest from the query box">
        <svg viewBox="-12 -14 24 26">
          <path d="M0,10 C-5,4 -7,1 -7,-3 A7,7 0 1 1 7,-3 C7,1 5,4 0,10 Z" class="lg-pin" />
          <circle cx="0" cy="-3" r="2.4" class="lg-pin-hole" />
        </svg>
        your POI
      </span>
      <span class="map-legend__item" title="The publication under the mouse in the table">
        <svg viewBox="-12 -12 24 24"><polygon :points="hex(9)" class="lg-hover" /></svg>
        hovered row
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { baseSdgColors, baseSdgTitles } from "@/constants/constants";

const props = defineProps({
  variant: { type: String as PropType<"publications" | "sdg">, default: "publications" },
  // Colour of the SDG world (variant "sdg")
  sdgColor: { type: String, default: "#888888" },
});

// Any other SDG colour, to show a mismatching outline
const otherColor = computed(() =>
  props.sdgColor.toLowerCase() === baseSdgColors[5].toLowerCase() ? baseSdgColors[0] : baseSdgColors[5],
);

const hex = (r: number, cx = 0) =>
  Array.from({ length: 6 }, (_, k) => {
    const a = (Math.PI / 3) * k;
    return `${(cx + r * Math.cos(a)).toFixed(2)},${(r * Math.sin(a)).toFixed(2)}`;
  }).join(" ");
const diamond = (r: number) => `0,${-r} ${r},0 0,${r} ${-r},0`;
</script>

<style scoped>
.map-legend {
  @apply flex flex-wrap items-center gap-x-5 gap-y-2 rounded-xl border border-line bg-surface-2/70 px-3 py-2;
}
.map-legend__group {
  @apply flex items-center gap-2.5;
}
.map-legend__key {
  @apply font-mono text-[10px] uppercase tracking-wider text-fg-faint;
}
.map-legend__item {
  @apply flex cursor-help items-center gap-1.5 whitespace-nowrap text-xs text-fg-dim;
}
.map-legend__item svg {
  @apply h-5 w-auto;
}
.map-legend__sdgs {
  @apply grid grid-cols-[repeat(17,7px)] gap-px;
}
.map-legend__sdgs span {
  @apply block h-2 w-[7px];
}
.lg-mark {
  fill: rgb(var(--c-fg-dim));
  stroke: rgb(var(--c-bg));
  stroke-width: 1;
}
.lg-mark--quest {
  stroke: rgb(var(--c-fg));
  stroke-width: 1.5;
}
.lg-ring {
  stroke-width: 2.5;
}
.lg-pin {
  fill: rgb(var(--c-blue));
}
.lg-pin-hole {
  fill: rgb(var(--c-bg));
}
.lg-hover {
  fill: none;
  stroke: rgb(var(--c-accent));
  stroke-width: 2;
}
</style>
