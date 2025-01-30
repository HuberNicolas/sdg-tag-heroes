<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-10 grid-cols-8 grid-flow-col h-full">
      <div class="row-span-1 col-span-2 bg-purple-400">
        <SDGSelector></SDGSelector>
      </div>
      <div class="row-span-9 col-span-2 bg-red-400">
        SHAP from Publication {{publicationId}}
        <ShapAbstract></ShapAbstract>
      </div>
      <div class="row-span-10 col-span-2 bg-blue-400">
        Annotations
        <ShapSelector></ShapSelector>
        <UDivider></UDivider>
        <ConnectingDots></ConnectingDots>
      </div>
      <div class="row-span-1 col-span-2 bg-pink-400">
        <div>Label Distribution</div>
        <BarLabelPlot :width="400" :height="100" />
      </div>

      <div class="row-span-1 col-span-4 bg-yellow-400">
        <CommentSummary></CommentSummary>
      </div>
      <div class="row-span-8 col-span-4 bg-orange-400">
        <CommentSection></CommentSection>
      </div>
      <div class="row-span-1 col-span-2 bg-green-400">
        <div>Placeholder</div>
        <UToggle
          on-icon="i-heroicons-check-20-solid"
          off-icon="i-heroicons-x-mark-20-solid"
          :model-value="false"
        />
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
