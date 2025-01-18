<template>
  <div id="app">
    <div class="source-boxes">
      <div id="1" class="box">1</div>
      <div id="2" class="box">2</div>
      <div id="3" class="box">3</div>
      <div id="4" class="box">4</div>
    </div>
    <div id="target-box" class="decision-box">Decision Box</div>
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

.source-boxes {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.box {
  width: 100px;
  height: 100px;
  background-color: lightblue;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  border: 2px solid blue;
  cursor: pointer;
}

.decision-box {
  width: 150px;
  height: 150px;
  background-color: lightgreen;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  border: 3px solid green;
}
</style>
