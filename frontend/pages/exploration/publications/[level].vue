<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-6 grid-cols-6 grid-flow-col h-full">
      <div class="row-span-5 col-span-5 bg-red-400">Exploration Map with params Level{{selectedLevel}}</div>
      <div class="row-span-1 col-span-5 bg-blue-400">Options</div>
      <div class="row-span-1 col-span-2 bg-green-400">Quests (Entropy Based)</div>
      <div class="row-span-5 col-span-2 bg-yellow-400">Publication List</div>
    </div>

  </div>
</template>

<script setup lang="ts">
const route = useRoute()

const selectedLevel = route.params.level


</script>

<style scoped>

</style>
