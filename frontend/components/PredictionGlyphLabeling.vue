<template>
  <div
    ref="glyphContainer"
    class="hex-glyph"
    :style="{ height: `${height}px`, width: `${width}px`, transform: transformStyle }"

  ></div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import createGlyph from "@/composables/glyph/predictionGlyphLabeling";

const props = defineProps({
  values: {
    type: Array as PropType<number[]>,
    required: true,
    default: () => Array(17).fill(0), // Default to an array of 17 zeros
    validator: (arr: number[]) => arr.length === 17, // Ensure 17 values
  },
  height: {
    type: Number,
    default: 50, // Default height of the glyph
  },
  width: {
    type: Number,
    default: 50, // Default width of the glyph
  },
  transformStyle: {
    type: String,
    default: "translate(-20%, -10%)", // Default transformation
  },
});

// Reactive reference to the container
const glyphContainer = ref<HTMLElement | null>(null);

// Use the prop directly
const { renderHexGrid } = createGlyph(props.values);

const renderGlyph = () => {
  if (glyphContainer.value) {
    renderHexGrid(glyphContainer.value, props.width, props.height);
  }
};

onMounted(() => {
  renderGlyph();
});


// Watch for changes in the `values` prop and re-render the glyph
watch(() => props.values, () => {
  renderGlyph();
}, { deep: true });
</script>

<style scoped>


.hex-glyph {
  display: inline-block;
  position: relative;
  /* transform: rotate(45deg); */
  aspect-ratio: 1 / 1;

  background: none !important;
  overflow: hidden; /* Prevent overflow */
}

</style>
