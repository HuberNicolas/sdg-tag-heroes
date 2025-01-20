<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-6 grid-cols-6 grid-flow-col h-full">
      <div class="row-span-4 col-span-4 bg-red-400">Exploration Map with params SDG{{selectedSDG}} - Level{{selectedLevel}}</div>
      <div class="row-span-2 col-span-4 bg-blue-400">Options</div>
      <div class="row-span-1 col-span-2 bg-green-400">Quests (Vote Based)</div>
      <div class="row-span-5 col-span-2 bg-yellow-400">Publication List</div>
    </div>

  </div>
</template>

<script setup lang="ts">
const route = useRoute()

const selectedSDG = route.params.sdg
const selectedLevel = route.params.level


</script>

<style scoped>

</style>
