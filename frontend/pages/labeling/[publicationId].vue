<template>
  <!-- Three areas: machine support, your contribution, community support.
       From 2xl on they sit side by side and fill the window. On xl, community support
       moves below the other two; smaller screens stack everything. -->
  <div class="min-h-full 2xl:h-full flex flex-col">
    <header class="flex-none border-b border-line px-4 py-3 flex flex-wrap items-center justify-between gap-2">
      <div>
        <p class="kicker">// labeling · publication #{{ publicationId }}</p>
        <h1 class="mt-1 text-lg 2xl:text-xl font-bold tracking-tight">Labeling with machine and community support</h1>
      </div>
      <div class="flex items-center gap-2">
        <span class="stat-pill"><Icon name="mdi:robot-outline" class="text-accent" />machine</span>
        <span class="stat-pill"><Icon name="mdi:account-edit-outline" class="text-accent" />you</span>
        <span class="stat-pill"><Icon name="mdi:account-group-outline" class="text-accent" />community</span>
      </div>
    </header>

    <div class="flex-1 min-h-0 grid grid-cols-1 xl:grid-cols-2 2xl:grid-cols-[3fr_3fr_4fr] gap-3 p-3">
      <!-- Machine support -->
      <section class="flex flex-col gap-3 min-h-0 min-w-0">
        <h2 class="section-head"><Icon name="mdi:robot-outline" />Machine Support</h2>
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
        <h2 class="section-head"><Icon name="mdi:account-edit-outline" />Your Contribution</h2>
        <AnnotationSection class="flex-1 min-h-0" />
      </section>

      <!-- Community support -->
      <section class="flex flex-col gap-3 min-h-0 min-w-0 xl:col-span-2 2xl:col-span-1">
        <h2 class="section-head"><Icon name="mdi:account-group-outline" />Community Support</h2>

        <div class="flex-none frame-container">
          <div class="flex flex-wrap items-center gap-2">
            <div class="frame-title"><b>Summarize</b> Community Labeling: Explore SDG Voting Trends</div>
            <div class="flex items-center gap-2 ml-auto">
              <label for="content-toggle" class="font-mono text-xs text-fg-dim">
                {{ showContent ? 'Hide Community Help' : 'Show Community Help' }}
              </label>
              <UToggle id="content-toggle" v-model="showContent" color="primary" />
            </div>
          </div>

          <div v-if="showContent" class="mt-2 flex flex-col gap-3">
            <!-- Key figures of the votes -->
            <div class="grid grid-cols-3 gap-2">
              <div class="kpi">
                <span class="kpi__key">labels</span>
                <span class="kpi__value">{{ labelDecisionsStore.totalVotes }}</span>
              </div>
              <div class="kpi" :style="leader ? { boxShadow: `inset 3px 0 0 ${leaderColor}` } : {}">
                <span class="kpi__key">leading</span>
                <span class="kpi__value truncate" :style="leader ? { color: leaderColor } : {}">
                  {{ leader ? (leader.label === -1 ? 'none' : `SDG ${leader.label}`) : '—' }}
                </span>
              </div>
              <div class="kpi">
                <span class="kpi__key">agreement</span>
                <span class="kpi__value">{{ leader ? `${Math.round(leaderShare * 100)}%` : '—' }}</span>
                <span class="kpi__bar"><span :style="{ width: `${Math.round(leaderShare * 100)}%` }" /></span>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-[auto_minmax(0,1fr)] gap-3 items-center">
              <div class="flex justify-center">
                <DonutPlot />
              </div>
              <div class="flex flex-col gap-2 min-w-0">
                <BarLabelPlot :height="110" :sort-descending="sortDescending" />
                <div class="flex flex-wrap items-center gap-x-5 gap-y-1.5">
                  <SDGUserLabelCheckbox class="shrink-0" />
                  <SortedOrderCheckbox v-model="sortDescending" class="shrink-0" />
                </div>
              </div>
            </div>
            <QuestIndicator />
          </div>
        </div>

        <!-- Below 2xl the page scrolls: the comments get a fixed height and scroll inside -->
        <div v-if="showContent" class="flex-1 h-[32rem] 2xl:h-auto min-h-0 frame-container flex flex-col">
          <div class="flex-none flex items-center justify-end gap-2">
            <Icon
              :name="showAnnotations ? 'mdi-tag' : 'mdi-comment-outline'"
              class="w-5 h-5 text-fg"
            />
            <label for="comment-toggle" class="font-mono text-xs text-fg-dim">
              {{ showAnnotations ? 'Show Community Labels' : 'Show Community Comments' }}
            </label>
            <UToggle id="comment-toggle" v-model="showAnnotations" color="primary" />
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
import BarLabelPlot from "~/components/plots/BarLabelPlot.vue";
import AnnotationSection from "~/components/AnnotationSection.vue";
import { computed, onMounted, ref } from "vue";
import DonutPlot from "~/components/plots/DonutPlot.vue";
import { Quadrant, Stage } from "~/types/enums";
import { useGameStore } from "~/stores/game";
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

// Key figures of the community votes (display only)
const leader = computed(() => {
  const entries = Object.entries(labelDecisionsStore.voteDistribution as Record<string, number>)
    .map(([label, count]) => ({ label: Number(label), count }))
    .sort((a, b) => b.count - a.count);
  return entries[0] ?? null;
});
const leaderShare = computed(() =>
  leader.value && labelDecisionsStore.totalVotes ? leader.value.count / labelDecisionsStore.totalVotes : 0,
);
const leaderColor = computed(() =>
  leader.value && leader.value.label !== -1 ? sdgsStore.getColorBySDG(leader.value.label) : "rgb(var(--c-fg-faint))",
);

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
.section-head {
  @apply flex flex-none items-center gap-2 font-mono text-xs font-semibold uppercase tracking-wider text-fg-dim;
}
.section-head :deep(svg) {
  @apply h-4 w-4 text-accent;
}
.kpi {
  @apply relative flex min-w-0 flex-col gap-0.5 rounded-xl border border-line bg-surface-2/70 px-3 py-2;
}
.kpi__key {
  @apply font-mono text-[10px] uppercase tracking-wider text-fg-faint;
}
.kpi__value {
  @apply font-mono text-lg font-semibold leading-tight text-fg;
}
.kpi__bar {
  @apply mt-1 block h-1 overflow-hidden rounded-full bg-muted-strong;
}
.kpi__bar span {
  @apply block h-full rounded-full bg-accent transition-[width] duration-500;
}
</style>
