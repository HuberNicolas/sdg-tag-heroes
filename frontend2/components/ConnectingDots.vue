<template>
  <div class="flex items-center justify-between">
    <!-- Left Glyph Container (Takes 4/5 of the screen) -->
    <div id="glyph-container" class="flex justify-center items-center w-4/5">

    </div>
    <Icon
      name="line-md-question"
      class="absolute w-[100px] h-[100px] text-gray-600 -translate-x-4"
    />



    <!-- Right Decision Hexagon (Takes 1/5 of the screen) -->
    <div id="target-container" class="relative flex justify-center items-center w-1/5">
      <p class="absolute left-4 top-14 text-gray-700 text-sm font-semibold">Your time to shine!</p>
      <Icon
        name="line-md-document"
        class="w-[200px] h-[200px] text-gray-600 opacity-20 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
      />
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
