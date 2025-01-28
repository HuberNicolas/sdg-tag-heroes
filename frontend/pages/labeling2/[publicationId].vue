<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-10 grid-cols-4 grid-flow-col h-full">
      <div class="row-span-1 col-span-2 bg-purple-400">
        <SDGSelector></SDGSelector>
      </div>
      <div class="row-span-9 col-span-1 bg-red-400">
        SHAP from Publication {{publicationId}}
        <ShapAbstract></ShapAbstract>
      </div>
      <div class="row-span-9 col-span-1 bg-blue-400">
        Annotations
        <ShapSelector></ShapSelector>
      </div>
      <div class="row-span-2 col-span-1 bg-yellow-400">
        Comment Summary
        <CommentSummary></CommentSummary>
      </div>
      <div class="row-span-8 col-span-1 bg-orange-400">
        <CommentSection></CommentSection>
      </div>
      <div class="row-span-2 col-span-1 bg-pink-400">
        <div>Label Distribution</div>
        <BarLabelPlot :width="500" :height="250" />
      </div>
      <div class="row-span-8 col-span-1 bg-green-400">
        <ConnectingDots></ConnectingDots>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import CommentSection from "~/components/CommentSection.vue";
import CommentSummary from "~/components/CommentSummary.vue"
import ShapSelector from "~/components/ShapSelector.vue";
import BarLabelPlot from "~/components/plots/BarLabelPlot.vue";

const route = useRoute()

const publicationId = route.params.publicationId

</script>

<style scoped>

</style>
