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

      <div class="row-span-2 col-span-3 bg-green-400">


        <div class="row-span-1 col-span-1 bg-blue-400 flex justify-evenly items-center">
          <div>
            <label for="content-toggle" class="mr-2 text-lg font-medium text-gray-700">Show User Labels</label>
            <input
              id="content-toggle"
              type="checkbox"
              class="toggle toggle-primary"
              v-model="showContent"
            />
          </div>

          <!-- Help -->

          <div class="drawer drawer-end">
            <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
            <div class="drawer-content">
              <!-- Page content here -->
              <label for="my-drawer-4" class="drawer-button btn btn-primary">Help</label>
            </div>
            <div class="drawer-side">
              <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
              <ul class="menu bg-base-200 text-base-content min-h-full w-80 p-4">
                <!-- Sidebar content here -->
                <li><a>Sidebar Item 1</a></li>
                <li><a>Sidebar Item 2</a></li>
              </ul>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-3">
          <div  v-if="showContent" class="row-span-1 col-span-1 bg-green-400">
            <DonutPlot></DonutPlot>
          </div>

          <div v-if="showContent" class="row-span-1 col-span-1 bg-orange-400">
            <SDGUserLabelToggle />
            <BarLabelPlot :width="200" :height="100" />
          </div>

          <div  v-if="showContent" class="row-span-1 col-span-1 bg-purple-400 flex justify-center items-center">
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
import DonutPlot from "~/components/plots/DonutPlot.vue";

const route = useRoute()

const publicationId = route.params.publicationId

const showAnnotations = ref(false); // State to toggle between components
const showContent = ref(false); // State to toggle the visibility of the sections

</script>

<style scoped>

</style>
