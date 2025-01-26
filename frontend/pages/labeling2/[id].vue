<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-6 grid-cols-4 grid-flow-col h-full">
      <div class="row-span-6 col-span-1 bg-red-400">
        SHAP from Publication {{publicationId}}
        <ShapAbstract></ShapAbstract>
      </div>
      <div class="row-span-6 col-span-1 bg-blue-400">Annotations</div>
      <div class="row-span-2 col-span-1 bg-yellow-400">Comment Summary</div>
      <div class="row-span-4 col-span-1 bg-orange-400">
        Vote list
      </div>
      <div class="row-span-6 col-span-1 bg-green-400">
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
