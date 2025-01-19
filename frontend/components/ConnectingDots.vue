<template>
  <div id="app">
    <div id="glyph-container" style="width: 500px; height: 500px;"></div>
    <div id="target-box" class="decision-box"></div>
  </div>
</template>

<script>
import useConnect from '@/composables/connect';

export default {
  setup() {
    const { fixedConnections } = useConnect();
    return { fixedConnections };
  },
};
</script>

<style>
#app {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 80%;
  margin: auto;
  margin-top: 50px;
}


</style>
