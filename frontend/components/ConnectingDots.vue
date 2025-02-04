<template>
  <div>
    <div id="glyph-container"></div>
    <div id="target-box" class="decision-box bg-red-900"></div>
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
