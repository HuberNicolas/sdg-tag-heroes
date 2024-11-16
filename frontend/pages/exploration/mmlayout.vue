<template>
  <div>
    <MinimapContainer></MinimapContainer>
    <BoxplotContainer></BoxplotContainer>
  </div>
</template>

<script>
import { defineComponent } from "vue";
import MinimapContainer from "~/components/MinimapContainer.vue";
import BoxplotContainer from "~/components/BoxplotContainer.vue";

export default defineComponent({
  components: { BoxplotContainer, MinimapContainer }
});
</script>


<style scoped>
</style>/
