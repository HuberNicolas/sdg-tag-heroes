<template>
  <!-- Three areas: machine support, your contribution, community support.
       From 2xl on they sit side by side and fill the window. On xl, community support
       moves below the other two; smaller screens stack everything. -->
  <div class="min-h-full 2xl:h-full flex flex-col">
    <header class="flex-none bg-gray-50 border-b border-gray-200 px-3 py-2 text-center">
      <h1 class="text-lg 2xl:text-xl font-bold flex items-center justify-center gap-2">
        <Icon name="mdi:robot-outline" class="text-gray-700 w-6 h-6" />
        <span>Labeling with machine and community support</span>
        <Icon name="mdi:account-group-outline" class="text-gray-700 w-6 h-6" />
      </h1>
    </header>

    <div class="flex-1 min-h-0 grid grid-cols-1 xl:grid-cols-2 2xl:grid-cols-[3fr_3fr_4fr] gap-3 p-3">
      <!-- Machine support -->
      <section class="flex flex-col gap-3 min-h-0 min-w-0">
        <h2 class="flex-none flex items-center justify-center gap-2 text-lg font-bold">
          <Icon name="mdi:robot-outline" class="text-gray-700 w-5 h-5" />
          Machine Support
        </h2>
        <div class="flex-none grid grid-cols-1 2xl:grid-cols-[3fr_2fr] gap-3">
          <SDGSelector />
          <div class="frame-container">
            <div class="frame-title"><b>Investigate</b> Machine Scores for each SDG</div>
            <div ref="glyphContainer" class="flex justify-center">
              <HexGlyph />
            </div>
          </div>
        </div>
        <SDGExplorerLabeling class="flex-none" />
        <ShapAbstract class="flex-1 min-h-[24rem] 2xl:min-h-0" />
      </section>

      <!-- Your contribution -->
      <section class="flex flex-col gap-3 min-h-0 min-w-0">
        <h2 class="flex-none text-center text-lg font-bold">Your Contribution</h2>
        <AnnotationSection class="flex-1 min-h-0" />
      </section>

      <!-- Community support -->
      <section class="flex flex-col gap-3 min-h-0 min-w-0 xl:col-span-2 2xl:col-span-1">
        <h2 class="flex-none flex items-center justify-center gap-2 text-lg font-bold">
          <Icon name="mdi:account-group-outline" class="text-gray-700 w-5 h-5" />
          Community Support
        </h2>

        <div class="flex-none frame-container">
          <div class="flex flex-wrap items-center gap-2">
            <div class="frame-title"><b>Summarize</b> Community Labeling: Explore SDG Voting Trends</div>
            <div class="flex items-center gap-2 ml-auto">
              <label for="content-toggle" class="text-sm font-medium text-gray-700">
                {{ showContent ? 'Hide Community Help' : 'Show Community Help' }}
              </label>
              <UToggle id="content-toggle" color="primary" v-model="showContent" />
            </div>
          </div>

          <div v-if="showContent" class="mt-2 grid grid-cols-1 2xl:grid-cols-3 gap-3 items-center">
            <div class="flex justify-center">
              <DonutPlot />
            </div>
            <div class="2xl:col-span-2 flex flex-col gap-2 min-w-0">
              <BarLabelPlot :height="100" :sortDescending="sortDescending" />
              <div class="flex flex-wrap justify-center items-center gap-x-8 gap-y-2">
                <SDGUserLabelCheckbox class="shrink-0" />
                <SortedOrderCheckbox v-model="sortDescending" class="shrink-0" />
              </div>
              <QuestIndicator />
            </div>
          </div>
        </div>

        <div v-if="showContent" class="flex-1 min-h-[24rem] 2xl:min-h-0 frame-container flex flex-col">
          <div class="flex-none flex items-center justify-end gap-2">
            <Icon
              :name="showAnnotations ? 'mdi-tag' : 'mdi-comment-outline'"
              class="w-5 h-5 text-gray-700"
            />
            <label for="comment-toggle" class="text-sm font-medium text-gray-700">
              {{ showAnnotations ? 'Show Community Labels' : 'Show Community Comments' }}
            </label>
            <UToggle v-model="showAnnotations" color="primary" id="comment-toggle" />
          </div>
          <div class="flex-1 min-h-0 overflow-y-auto">
            <CommentSection v-if="!showAnnotations" />
            <CommentSectionAnnotations v-else />
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">

import CommentSection from "~/components/CommentSection.vue";
import CommentSummary from "~/components/CommentSummary.vue";
import BarLabelPlot from "~/components/plots/BarLabelPlot.vue";
import AnnotationSection from "~/components/AnnotationSection.vue";
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
