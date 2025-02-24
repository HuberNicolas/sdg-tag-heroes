<template>
  <div class="h-full overflow-hidden">
    <div class="grid grid-rows-12 grid-cols-10 grid-flow-col h-full overflow-hidden">

      <!-- Overarching Title -->
      <div class="row-span-1 col-span-10 flex flex-col items-center justify-center text-center bg-gray-50 py-1 min-h-fit leading-none">
        <h1 class="text-xl font-bold w-full flex items-center justify-center space-x-2">
          <Icon name="mdi:robot-outline" class="text-gray-700 w-6 h-6" />
          <span>Tagging with machine and community support</span>
          <Icon name="mdi:account-group-outline" class="text-gray-700 w-6 h-6" />
        </h1>

        <div class="grid grid-cols-10 w-full text-center">
          <!-- Machine Support -->
          <div class="col-span-3 flex items-center justify-center space-x-2">
            <Icon name="mdi:robot-outline" class="text-gray-700 w-5 h-5" />
            <p class="text-xl"><b>Machine Support</b></p>
          </div>

          <!-- Your Decision -->
          <div class="col-span-3 flex items-center justify-center">
            <p class="text-xl"><b>Your</b> Decision</p>
          </div>

          <!-- Community Support -->
          <div class="col-span-4 flex items-center justify-center space-x-2">
            <Icon name="mdi:account-group-outline" class="text-gray-700 w-5 h-5" />
            <p class="text-xl"><b>Community Support</b></p>
          </div>
        </div>
      </div>


      <div class="row-span-4 col-span-3">
        <div class="grid grid-cols-6 grid-rows-2">
          <div class="col-span-4 row-span-1">
            <SDGSelector></SDGSelector>
          </div>

          <div class="col-span-2 row-span-1">
            <div class="frame-container">
              <div class="frame-title"><b>Investigate</b> machine scores for each SDG</div>
              <div ref="glyphContainer">
                <HexGlyph />
              </div>
            </div>
          </div>

          <div class="col-span-6 row-span-1">
            <SDGExplorerLabeling></SDGExplorerLabeling>
          </div>
        </div>
      </div>

      <div class="row-span-7 col-span-3 flex flex-col h-full overflow-hidden">
        <ShapAbstract></ShapAbstract>
      </div>


      <div class="row-span-11 col-span-3">
        <AnnotationSection></AnnotationSection>
      </div>


      <div class="row-span-3 col-span-5">
        <div class="flex justify-evenly items-start">
          <div class="frame-container w-full">
            <div class="flex items-center">
              <div class="frame-title"><b>Summarize</b> Community Labeling: Explore SDG Voting Trends</div>
              <div class="flex items-center justify-end space-x-2 ml-auto">
                <label for="content-toggle" class="text-lg font-medium text-gray-700">
                  {{ showContent ? 'Hide Community Help' : 'Show Community Help' }}
                </label>
                <UToggle id="content-toggle" color="primary" v-model="showContent" />
              </div>
            </div>

            <div class="grid grid-cols-3 grid-rows-4">

              <div class="col-span-1 row-span-4" v-if="showContent">
                <DonutPlot></DonutPlot>
              </div>

              <!-- SDG Bar Chart Section -->
              <div class="col-span-2 row-span-1 flex flex-col justify-between" v-if="showContent">
                <div class="flex flex-col items-center">
                  <!-- Centered Bar Chart -->
                  <BarLabelPlot :width="500" :height="100" :sortDescending="sortDescending" />

                  <!-- Centered Controls Below the Chart -->
                  <div class="flex justify-center items-center space-x-8">
                    <SDGUserLabelCheckbox class="shrink-0" />
                    <SortedOrderCheckbox v-model="sortDescending" class="shrink-0" />
                  </div>
                </div>
              </div>

              <div class="col-span-2 flex items-center px-2 p-y0.5" v-if="showContent">
                  <QuestIndicator />
              </div>

            </div>
          </div>
        </div>
      </div>

      <div class="row-span-8 col-span-5 flex flex-col justify-center items-center overflow-hidden">
        <div v-if="showContent" class="overflow-hidden h-full w-full" >
          <!-- Conditional Rendering -->
          <div class="frame-container overflow-hidden">
            <!-- Toggle Switch -->
            <div class="flex items-center justify-end space-x-2">
              <Icon
                :name="showAnnotations ? 'mdi-tag' : 'mdi-comment-outline'"
                class="w-5 h-5 text-gray-700"
              />
              <label for="comment-toggle" class="text-lg font-medium text-gray-700">
                {{ showAnnotations ? 'Show Community Labels' : 'Show Community Comments' }}
              </label>
              <UToggle v-model="showAnnotations" color="primary" id="comment-toggle" />
            </div>
            <div v-if="!showAnnotations" class="overflow-hidden">
              <CommentSection  class="overflow-hidden" />
            </div>
            <div v-else class="overflow-hidden">
              <CommentSectionAnnotations class="overflow-hidden" />
            </div>
          </div>
        </div>
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
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users";
import { useSDGsStore } from "~/stores/sdgs";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import HexGlyph from "~/components/PredictionGlyphLabeling.vue";

const gameStore = useGameStore();
const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();
const sdgsStore = useSDGsStore();
const rankStore = useSDGRanksStore();

const route = useRoute()

const publicationId = route.params.publicationId

const showAnnotations = ref(false); // State to toggle between components
const showContent = ref(false); // State to toggle the visibility of the sections
const sortDescending = ref(false);

onMounted(async () => {
  gameStore.setStage(Stage.LABELING);
  gameStore.setQuadrant(Quadrant.ONE_PUB_ALL_SDG);

  await labelDecisionsStore.fetchUserLabelsByPublicationId(publicationId);
  await labelDecisionsStore.fetchSDGLabelDecisionByPublicationId(publicationId);
  await usersStore.fetchUsers(); // Fetch users for avatars
  await sdgsStore.fetchSDGs(); // Fetch SDGs for icons
  await rankStore.fetchSDGRanksForUsers(); // For user rank info
})

</script>

<style scoped>

</style>
