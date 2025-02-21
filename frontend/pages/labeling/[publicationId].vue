<template>
  <div class="h-full overflow-hidden">
    <div class="grid grid-rows-12 grid-cols-10 grid-flow-col h-full">

      <!-- Overarching Title -->
      <div class="row-span-1 col-span-10 flex flex-col items-center justify-center text-center bg-gray-50 py-1 min-h-fit leading-none">
      <h1 class="text-xl font-bold w-full">Tagging with machine and community support</h1>
        <div class="grid grid-cols-10 w-full text-center">
          <div class="col-span-3 flex items-center justify-center">
            <p class="text-xl"><b>Machine Support</b></p>
          </div>
          <div class="col-span-3 flex items-center justify-center">
            <p class="text-xl"><b>Your</b> Decision</p>
          </div>
          <div class="col-span-4 flex items-center justify-center">
            <p class="text-xl"><b>Community Support</b></p>
          </div>
        </div>
      </div>

      <div class="row-span-3 col-span-3">

        <div class="grid grid-cols-6 grid-rows-2">
          <div class="col-span-3 row-span-2">
            <SDGSelector></SDGSelector>
          </div>
          <div class="col-span-3 row-span-2">
            <SDGExplorerLabeling></SDGExplorerLabeling>
          </div>
          <!-- <HexGlyph :values=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] :height="260" :width="260" /> -->
        </div>
      </div>

      <div class="row-span-8 col-span-3">
        <ShapAbstract></ShapAbstract>
      </div>


      <div class="row-span-11 col-span-3">
        <AnnotationSection></AnnotationSection>
      </div>


      <div class="row-span-2 col-span-3">
        <div class="row-span-1 col-span-1 flex justify-evenly items-center">
          <div>
            <label for="content-toggle" class="mr-2 text-lg font-medium text-gray-700">Show Community Votes</label>
            <input
              id="content-toggle"
              type="checkbox"
              class="toggle toggle-primary"
              v-model="showContent"
            />
          </div>
        </div>
        <div class="grid grid-cols-4">
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

      <div v-if="showContent" class="row-span-1 col-span-4">
        <CommentSummary></CommentSummary>
      </div>

      <div v-if="showContent" class="row-span-8 col-span-4 flex flex-col justify-center items-center">
        <!-- Toggle Switch -->
        <div class="flex items-center justify-center mb-4">
          <label for="comment-toggle" class="mr-2 text-lg font-medium text-gray-700">Show Community Comments</label>
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
