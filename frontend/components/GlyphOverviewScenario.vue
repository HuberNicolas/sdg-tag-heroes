<template>
  <!-- The SVG uses a viewBox, so it scales with this square container -->
  <div ref="glyphContainer" class="hex-glyph aspect-square"/>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import createGlyph from "@/composables/glyph/predictionOverviewGlyph";

const props = defineProps({
  values: {
    type: Array as PropType<number[]>,
    required: true,
    default: () => Array(17).fill(0),
    validator: (arr: number[]) => arr.length === 17,
  },
});

const glyphContainer = ref<HTMLElement | null>(null);

const { renderHexGrid } = createGlyph(props.values);

onMounted(() => {
  if (glyphContainer.value) {
    renderHexGrid(glyphContainer.value, "100%", "100%");
  }
});
</script>
