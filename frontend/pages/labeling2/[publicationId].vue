<template>
  <div class="h-full overflow-hidden">
    <div class="grid grid-rows-10 grid-cols-10 grid-flow-col h-full">

      <div class="row-span-2 col-span-3">
        <div class="grid grid-cols-4">
          <div class="col-span-3">
            <SDGSelector></SDGSelector>
          </div>
          <div class="col-span-1">
            <SDGExplorerLabeling></SDGExplorerLabeling>

          </div>
        </div>


      </div>


      <div class="row-span-8 col-span-3">
        <ShapToggle />
        <ShapAbstract></ShapAbstract>
      </div>




      <div class="row-span-10 col-span-4">
        <AnnotationSection></AnnotationSection>
        <div class="flex justify-between">
          <ContinueLabelingDialog></ContinueLabelingDialog>
          <ContinueExplorationDialog></ContinueExplorationDialog>
        </div>
      </div>






      <div class="row-span-2 col-span-3">
        <div class="row-span-1 col-span-1 flex justify-evenly items-center">
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
          <div  v-if="showContent" class="row-span-1 col-span-1">
            <DonutPlot></DonutPlot>
          </div>

          <div v-if="showContent" class="row-span-1 col-span-1">
            <SDGUserLabelToggle />
            <BarLabelPlot :width="200" :height="100" />
          </div>

          <div  v-if="showContent" class="row-span-1 col-span-1  flex justify-center items-center">
            <QuestIndicator></QuestIndicator>
          </div>
        </div>


      </div>

      <div v-if="showContent" class="row-span-1 col-span-3">
        <!-- <CommentSummary></CommentSummary> -->
      </div>



      <div v-if="showContent" class="row-span-7 col-span-3">
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
import CommentSummary from "~/components/CommentSummary.vue";
import BarLabelPlot from "~/components/plots/BarLabelPlot.vue";
import AnnotationSection from "~/components/AnnotationSection.vue";
import SDGUserLabelToggle from "~/components/SDGUserLabelToggle.vue";
import { onMounted, ref } from "vue";
import DonutPlot from "~/components/plots/DonutPlot.vue";
import { Quadrant, Stage } from "~/types/enums";
import { useGameStore } from "~/stores/game";
import ContinueLabelingDialog from "~/components/ContinueLabelingDialog.vue";
import ContinueExplorationDialog from "~/components/ContinueExplorationDialog.vue";
import SDGExplorerLabeling from "~/components/SDGExplorerLabeling.vue";

const gameStore = useGameStore();

const route = useRoute()

const publicationId = route.params.publicationId

const showAnnotations = ref(false); // State to toggle between components
const showContent = ref(false); // State to toggle the visibility of the sections


onMounted(() => {
  gameStore.setStage(Stage.LABELING);
  gameStore.setQuadrant(Quadrant.ONE_PUB_ALL_SDG);
})

</script>

<style scoped>

</style>
