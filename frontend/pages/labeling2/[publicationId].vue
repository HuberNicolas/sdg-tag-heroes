<template>
  <div class="flex flex-col h-screen">
    <div class="grid grid-rows-10 grid-cols-10 grid-flow-col h-full">
      <div class="row-span-1 col-span-3 bg-purple-400">
        <SDGSelector></SDGSelector>
      </div>
      <div class="row-span-9 col-span-3 bg-red-400">
        SHAP from Publication {{publicationId}}
        <ShapAbstract></ShapAbstract>
      </div>
      <div class="row-span-10 col-span-4 bg-blue-400">
        <AnnotationSection></AnnotationSection>
      </div>

      <div class="row-span-1 col-span-3 bg-green-400">
        <label for="content-toggle" class="mr-2 text-lg font-medium text-gray-700">Show User Labels</label>
        <input
          id="content-toggle"
          type="checkbox"
          class="toggle toggle-primary"
          v-model="showContent"
        />
      </div>



      <div class="row-span-1 col-span-3">
        <div class="grid grid-cols-3 gap-4">

          <div v-if="showContent" class="row-span-1 col-span-2 bg-pink-400">
            <SDGUserLabelToggle />
            <BarLabelPlot :width="400" :height="100" />
          </div>
          <div  v-if="showContent" class="row-span-1 col-span-1 bg-green-400">
            <QuestIndicator></QuestIndicator>
          </div>
        </div>
      </div>

      <div v-if="showContent" class="row-span-1 col-span-3 bg-yellow-400">
        <CommentSummary></CommentSummary>
      </div>



      <div v-if="showContent" class="row-span-7 col-span-3 bg-orange-400">
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
const showContent = ref(false); // State to toggle the visibility of the sections

</script>

<style scoped>

</style>
