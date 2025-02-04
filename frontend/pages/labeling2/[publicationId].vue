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
        <AnnotationSection></AnnotationSection>
      </div>
      <div class="row-span-1 col-span-2 bg-pink-400">
        <SDGUserLabelToggle />
        <BarLabelPlot :width="400" :height="100" />
      </div>

      <div class="row-span-1 col-span-4 bg-yellow-400">
        <CommentSummary></CommentSummary>

      </div>
      <div class="row-span-8 col-span-4 bg-orange-400">
        <!-- Toggle Switch -->
        <div class="flex justify-start items-center mb-4">
          <label for="comment-toggle" class="mr-2 text-lg font-medium text-gray-700">Show Annotations</label>
          <input
            id="comment-toggle"
            type="checkbox"
            class="toggle toggle-primary"
            v-model="showAnnotations"
          />
        </div>

        <!-- Conditional Rendering -->
        <CommentSection v-if="!showAnnotations" />
        <CommentSectionAnnotations v-else />
     </div>
     <div class="row-span-1 col-span-2 bg-green-400">
       <QuestIndicator></QuestIndicator>
       <UToggle
         on-icon="i-heroicons-check-20-solid"
         off-icon="i-heroicons-x-mark-20-solid"
         :model-value="false"
       />
       <div class="badge badge-outline">default</div>
       <div class="badge badge-primary badge-outline">primary</div>
       <div class="badge badge-secondary badge-outline">secondary</div>
       <div class="badge badge-accent badge-outline">accent</div>
     </div>
   </div>
 </div>
</template>

<script setup lang="ts">

import CommentSection from "~/components/CommentSection.vue";
import CommentSummary from "~/components/CommentSummary.vue"
import BarLabelPlot from "~/components/plots/BarLabelPlot.vue";
import AnnotationSection from "~/components/AnnotationSection.vue";
import SDGUserLabelToggle from "~/components/SDGUserLabelToggle.vue";
import { ref } from 'vue';

const route = useRoute()

const publicationId = route.params.publicationId

const showAnnotations = ref(false); // State to toggle between components

</script>

<style scoped>

</style>
