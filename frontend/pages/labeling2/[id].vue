<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-6 grid-cols-4 grid-flow-col h-full">
      <div class="row-span-5 col-span-1 bg-red-400">SHAP from Publication {{publicationId}}</div>
      <div class="row-span-1 col-span-4 bg-blue-400">
        Decision
      </div>
      <div class="row-span-5 col-span-1 bg-green-400">Annotations</div>
      <div class="row-span-1 col-span-2 bg-yellow-400">Comment Summary</div>
      <div class="row-span-4 col-span-2 bg-orange-400">
        Vote list
        <ConnectingDots></ConnectingDots>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

const route = useRoute()

const publicationId = route.params.id

</script>

<style scoped>

</style>
