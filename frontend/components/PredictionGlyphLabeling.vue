<template>
  <div
    ref="glyphContainer"
    class="hex-glyph"
    :style="{ height: `${height}px`, width: `${width}px`, transform: transformStyle }"
  ></div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useSDGsStore } from "~/stores/sdgs";
import createGlyph from "@/composables/glyph/predictionGlyphLabeling";

const props = defineProps({
  height: {
    type: Number,
    default: 200, // Default height of the glyph
  },
  width: {
    type: Number,
    default: 200, // Default width of the glyph
  },
  transformStyle: {
    type: String,
    default: "translate(-10%, 2.5%)", // Default transformation
  },
});

// Reactive reference to the container
const glyphContainer = ref<HTMLElement | null>(null);
const route = useRoute();
const publicationId = ref<number | null>(route.params.publicationId ? Number(route.params.publicationId) : null);
const sdgsStore = useSDGsStore();
const { selectedSDG } = storeToRefs(sdgsStore);

// Use the composable
const { renderHexGrid } = createGlyph();

// Render glyph on mount
onMounted(() => {
  if (glyphContainer.value) {
    renderHexGrid(glyphContainer.value, props.width, props.height, publicationId.value);
  }
});

// Watch for changes in publicationId and re-render
watch([publicationId, selectedSDG], () => {
  if (glyphContainer.value && publicationId.value) {
    renderHexGrid(glyphContainer.value, props.width, props.height, publicationId.value);
  }
});
</script>
