<template>
  <div
    ref="glyphContainer"
    class="hex-glyph"
    :style="glyphStyles"
  ></div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import createGlyph from "@/composables/glyph/predictionOverviewGlyph";

const props = defineProps({
  values: {
    type: Array as PropType<number[]>,
    required: true,
    default: () => Array(17).fill(0),
    validator: (arr: number[]) => arr.length === 17,
  },
  height: {
    type: Number,
    default: 50,
  },
  width: {
    type: Number,
    default: 50,
  },
});

const glyphContainer = ref<HTMLElement | null>(null);

const { renderHexGrid } = createGlyph(props.values);

// Calculate styles dynamically
const glyphStyles = computed(() => {
  return {
    height: `${props.height}px`,
    width: `${props.width}px`,
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-220%, -90%)',
  };
});

onMounted(() => {
  if (glyphContainer.value) {
    renderHexGrid(glyphContainer.value, props.width, props.height);
  }
});
</script>

<style scoped>
.hex-glyph {
  position: absolute;
}
</style>
