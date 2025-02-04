<template>
  <div class="flex items-center justify-between">
    <!-- Left Glyph Container (Takes 4/5 of the screen) -->
    <div id="glyph-container" class="flex justify-center items-center w-4/5"></div>

    <!-- Right Decision Hexagon (Takes 1/5 of the screen) -->
    <div id="target-container" class="relative flex justify-center items-center w-1/5">
      <div id="target-box" class="flex justify-center items-center relative z-20 overflow-visible"></div>
    </div>
  </div>
</template>

<script>
import useConnect from '@/composables/plots/connect';

export default {
  setup() {
    const { fixedConnections } = useConnect();
    return { fixedConnections };
  },
};
</script>
