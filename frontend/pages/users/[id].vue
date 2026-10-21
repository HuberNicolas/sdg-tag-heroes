<template>
  <!-- From lg on, the page fills the window: list of decisions on the left, details on the right; both scroll inside -->
  <div class="min-h-full lg:h-full flex flex-col">
    <header class="flex-none border-b border-line px-4 py-3 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <img
          v-if="profileUser?.email"
          :src="generateAvatar(profileUser.email)"
          :alt="`Avatar of ${profileUser.nickname}`"
          class="h-11 w-11 rounded-full ring-2 ring-accent/40 ring-offset-2 ring-offset-bg"
        >
        <div>
          <p class="kicker">// profile · label decisions</p>
          <h1 class="mt-0.5 text-lg 2xl:text-xl font-bold tracking-tight">{{ profileUser?.nickname || `User ${userId}` }}</h1>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <span class="stat-pill"><Icon name="mdi-scale-balance" class="text-accent" />decisions <b>{{ userSDGLabelDecisions.length }}</b></span>
        <span class="stat-pill"><Icon name="mdi-tag-outline" class="text-accent" />own labels <b>{{ ownLabelCount }}</b></span>
      </div>
    </header>

    <div class="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[minmax(17rem,24rem)_minmax(0,1fr)] gap-3 p-3">
      <!-- Sidebar: List of Label Decisions -->
      <aside class="frame-container flex flex-col min-h-[20rem] lg:min-h-0">
        <div class="frame-title"><b>Label decisions</b> on publications this person labeled or discussed</div>
        <LoadingState v-if="loading || (labelDecisionsStore.isLoading && !userSDGLabelDecisions.length)" label="loading decisions" />
        <p v-else-if="!userSDGLabelDecisions.length" class="py-8 text-center font-mono text-xs text-fg-dim">no label decisions yet</p>
        <ul v-else class="flex-1 min-h-0 overflow-y-auto space-y-1.5 pr-1">
          <li v-for="decision in userSDGLabelDecisions" :key="decision.decisionId">
            <button
              type="button"
              class="decision-item"
              :class="{ 'is-active': decision.decisionId === selectedDecisionId }"
              :style="{ '--sdg': decisionColor(decision) }"
              @click="selectedDecisionId = decision.decisionId"
            >
              <span class="decision-item__hex hex-clip" :title="decisionLabelText(decision)">{{ decisionBadge(decision) }}</span>
              <span class="min-w-0 flex-1">
                <span class="decision-item__title">{{ publicationTitles[decision.publicationId] || `Publication ${decision.publicationId}` }}</span>
                <span class="mt-0.5 block font-mono text-[11px] text-fg-faint">
                  #{{ decision.decisionId }} · {{ decision.userLabels?.length || 0 }} labels<template v-if="decision.scenarioType"> · {{ decision.scenarioType }}</template>
                </span>
              </span>
            </button>
          </li>
        </ul>
      </aside>

      <!-- Main Content: Label Decision Details -->
      <section class="flex flex-col gap-3 min-h-0 lg:overflow-y-auto lg:pr-1">
        <div v-if="!selectedDecision" class="frame-container flex flex-1 flex-col items-center justify-center gap-2 py-16 text-center">
          <Icon name="mdi-hexagon-multiple-outline" class="h-9 w-9 text-accent" />
          <p class="font-mono text-sm text-fg-dim">Select a label decision to view details.</p>
        </div>

        <template v-else>
          <!-- Decision header -->
          <div class="frame-container" :style="{ boxShadow: `inset 3px 0 0 ${decisionColor(selectedDecision)}, var(--shadow)` }">
            <p class="kicker">// decision #{{ selectedDecision.decisionId }} · publication #{{ selectedDecision.publicationId }}</p>
            <h2 class="mt-1.5 text-xl font-bold leading-snug tracking-tight">
              {{ publicationTitles[selectedDecision.publicationId] || `Publication ${selectedDecision.publicationId}` }}
            </h2>
            <div class="mt-3 flex flex-wrap items-center gap-2">
              <span class="decision-chip" :style="{ '--sdg': decisionColor(selectedDecision) }">
                <img v-if="getSDGIcon(selectedDecision.decidedLabel)" :src="getSDGIcon(selectedDecision.decidedLabel)" alt="" class="h-5 w-5 rounded">
                {{ decisionLabelText(selectedDecision) }}
              </span>
              <span v-if="selectedDecision.scenarioType" class="stat-pill">
                <span class="quest-gem !h-5 !w-5"><Icon name="i-heroicons-flag" /></span>{{ selectedDecision.scenarioType }}
              </span>
              <span v-if="selectedDecision.decisionType" class="stat-pill">{{ selectedDecision.decisionType.toLowerCase().replaceAll('_', ' ') }}</span>
              <span v-if="selectedDecision.createdAt" class="stat-pill">{{ new Date(selectedDecision.createdAt).toLocaleDateString() }}</span>
            </div>

            <!-- Contributors Section -->
            <div v-if="getContributors(selectedDecision).length" class="mt-4 flex items-center gap-3">
              <span class="font-mono text-[11px] uppercase tracking-wider text-fg-faint">contributors</span>
              <div class="flex -space-x-2">
                <NuxtLink
                  v-for="user in getContributors(selectedDecision)"
                  :key="user.userId"
                  :to="`/users/${user.userId}`"
                  class="relative group"
                  :title="`${user.nickname} · ${getSDGTitle(getUserVotedSDG(user.userId))} · rank ${getUserRank(user.userId)?.name || 'unranked'}`"
                >
                  <div
                    :style="{ borderColor: getSDGColor(getUserVotedSDG(user.userId)) }"
                    :class="['w-10 h-10 rounded-full border-[3px] bg-surface flex items-center justify-center transition-transform group-hover:-translate-y-0.5', getBorderStyle(getUserRank(user.userId)?.tier)]"
                  >
                    <img :src="generateAvatar(user.email)" class="w-8 h-8 rounded-full" :alt="`Avatar of ${user.name}`">
                  </div>
                </NuxtLink>
              </div>
            </div>
          </div>

          <!-- SDG labels of the publication -->
          <div class="frame-container">
            <div class="frame-title"><b>Summarize</b> the SDG labels of this publication</div>
            <LoadingState v-if="isLoading" size="sm" label="loading labels" />
            <template v-else-if="sdgLabelSummary && sdgs.length">
              <div class="grid grid-cols-[repeat(auto-fill,minmax(3.6rem,1fr))] gap-2">
                <div
                  v-for="sdg in sdgs"
                  :key="sdg.id"
                  class="sdg-state"
                  :class="sdg.label === 1 ? 'is-yes' : sdg.label === -1 ? 'is-no' : 'is-open'"
                  :style="{ '--sdg': sdg.color }"
                  :title="`SDG ${sdg.id}: ${sdg.label === 1 ? 'relevant' : sdg.label === -1 ? 'not relevant' : 'not rated'}`"
                >
                  <span class="sdg-state__hex hex-clip">{{ sdg.label === -1 ? '✕' : sdg.label === 1 ? sdg.id : '?' }}</span>
                  <span class="font-mono text-[11px] text-fg-dim">SDG {{ sdg.id }}</span>
                </div>
              </div>
              <p class="mt-2 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[11px] text-fg-faint">
                <span>coloured: relevant</span><span>✕: not relevant</span><span>?: not rated</span>
              </p>
            </template>
            <p v-else class="font-mono text-xs text-fg-dim">no label summary for this publication</p>
          </div>

          <!-- User Labels -->
          <div class="frame-container">
            <div class="frame-title"><b>Explore</b> the labels: who voted for which SDG and why</div>
            <p v-if="!selectedDecision.userLabels?.length" class="font-mono text-xs text-fg-dim">no labels yet</p>
            <ul v-else class="space-y-2">
              <li v-for="label in selectedDecision.userLabels" :key="label.labelId" class="entry" :style="{ '--sdg': getSDGColor(label.votedLabel) }">
                <div
                  :style="{ borderColor: getSDGColor(label.votedLabel) }"
                  :class="['h-11 w-11 flex-none rounded-full border-[3px] flex items-center justify-center', getBorderStyle(getUserRankForSDG(label.userId, label.votedLabel)?.tier)]"
                >
                  <img :src="generateAvatar(getUserById(label.userId)?.email)" alt="" class="h-9 w-9 rounded-full">
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <NuxtLink :to="`/users/${label.userId}`" class="font-semibold text-fg hover:text-accent">{{ getUserName(label.userId) }}</NuxtLink>
                    <span class="inline-flex items-center gap-1 rounded-full border border-line px-2 py-0.5 text-xs">
                      <img v-if="getSDGIcon(label.votedLabel)" :src="getSDGIcon(label.votedLabel)" :alt="`SDG ${label.votedLabel}`" class="h-4 w-4 rounded-sm">
                      {{ label.votedLabel === -1 ? 'not relevant' : `SDG ${label.votedLabel}` }}
                    </span>
                    <span class="inline-flex items-center gap-1 font-mono text-[11px] text-fg-dim">
                      <!-- Rank Symbol -->
                      <Icon
                        v-if="getUserRankForSDG(label.userId, label.votedLabel)?.tier === 1"
                        name="line-md:chevron-up"
                        class="w-4 h-4"
                        :style="{ color: getSDGColor(label.votedLabel) }"
                      />
                      <Icon
                        v-else-if="getUserRankForSDG(label.userId, label.votedLabel)?.tier === 2"
                        name="line-md:chevron-double-up"
                        class="w-4 h-4"
                        :style="{ color: getSDGColor(label.votedLabel) }"
                      />
                      <Icon
                        v-else-if="getUserRankForSDG(label.userId, label.votedLabel)?.tier === 3"
                        name="line-md:chevron-triple-up"
                        class="w-4 h-4"
                        :style="{ color: getSDGColor(label.votedLabel) }"
                      />
                      {{ getUserRankForSDG(label.userId, label.votedLabel)?.name || 'unranked' }}
                    </span>
                    <span v-if="label.votes?.length" class="font-mono text-[11px] text-fg-faint">{{ label.votes.length }} votes</span>
                  </div>
                  <p v-if="label.comment" class="mt-1 text-sm text-fg">{{ label.comment }}</p>
                  <p v-if="label.abstractSection" class="mt-1 border-l-2 border-line-strong pl-2 text-xs italic text-fg-dim">“{{ label.abstractSection }}”</p>
                </div>
              </li>
            </ul>
          </div>

          <!-- Annotations -->
          <div class="frame-container">
            <div class="frame-title"><b>Browse</b> the annotations on the abstract</div>
            <p v-if="!selectedDecision.annotations?.length" class="font-mono text-xs text-fg-dim">no annotations yet</p>
            <ul v-else class="space-y-2">
              <li v-for="annotation in selectedDecision.annotations" :key="annotation.annotationId" class="entry" :style="{ '--sdg': getSDGColor(getUserVotedSDG(annotation.userId)) }">
                <div
                  :style="{ borderColor: getSDGColor(getUserVotedSDG(annotation.userId)) }"
                  :class="['h-10 w-10 flex-none rounded-full border-[3px] flex items-center justify-center', getBorderStyle(getUserRank(annotation.userId)?.tier)]"
                >
                  <img :src="getUserAvatar(annotation.userId)" class="h-8 w-8 rounded-full" :alt="getUserName(annotation.userId)">
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <NuxtLink :to="`/users/${annotation.userId}`" class="font-semibold text-fg hover:text-accent">{{ getUserName(annotation.userId) }}</NuxtLink>
                    <span class="font-mono text-[11px] text-fg-faint">score {{ annotation.labelerScore }}</span>
                  </div>
                  <p class="mt-1 text-sm text-fg">{{ annotation.comment }}</p>
                </div>
              </li>
            </ul>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { useUsersStore } from "~/stores/users";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";
import { generateAvatar } from "~/utils/avatar";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { useSDGLabelSummariesStore } from "~/stores/sdgLabelSummaries";
import usePublications from "~/composables/usePublications";


// Router
const route = useRoute();
const userId = computed(() => Number(route.params.id));

// Stores
const usersStore = useUsersStore();
const labelDecisionsStore = useLabelDecisionsStore();
const sdgsStore = useSDGsStore();
const rankStore = useSDGRanksStore();
const sdgLabelSummariesStore = useSDGLabelSummariesStore();

const loading = ref(true);
const error = ref<string | null>(null);

const isLoading = computed(() => sdgLabelSummariesStore.isLoading || sdgsStore.isLoading);
const sdgLabelSummary = computed(() => sdgLabelSummariesStore.sdgLabelSummaryForPublication);

// Store data
const userSDGLabelDecisions = computed(() => labelDecisionsStore.userSDGLabelDecisions);
const selectedDecisionId = ref<number | null>(null);

// Display helpers
const profileUser = computed(() => usersStore.users.find((user) => user.userId === userId.value) || null);
const ownLabelCount = computed(() =>
  userSDGLabelDecisions.value.flatMap((decision) => decision.userLabels || []).filter((label) => label.userId === userId.value).length
);
const decisionColor = (decision) =>
  decision?.decidedLabel >= 1 ? getSDGColor(decision.decidedLabel) : "rgb(var(--c-fg-faint))";
const decisionBadge = (decision) => (decision.decidedLabel >= 1 ? decision.decidedLabel : decision.decidedLabel === -1 ? "✕" : "?");
const decisionLabelText = (decision) =>
  decision.decidedLabel >= 1
    ? `SDG ${decision.decidedLabel} · ${getSDGTitle(decision.decidedLabel)}`
    : decision.decidedLabel === -1
      ? "Not relevant"
      : "Open, no decision yet";

// Publication titles for the list (one request for all decisions)
const { getPublicationsByIds } = usePublications();
const publicationTitles = ref<Record<number, string>>({});
watch(userSDGLabelDecisions, async (decisions) => {
  const ids = [...new Set(decisions.map((decision) => decision.publicationId))].filter((id) => !(id in publicationTitles.value));
  if (ids.length) {
    try {
      const publications = await getPublicationsByIds(ids);
      publicationTitles.value = { ...publicationTitles.value, ...Object.fromEntries(publications.map((p) => [p.publicationId, p.title])) };
    } catch (err) {
      console.error("Failed to load publication titles", err);
    }
  }
  // Open the first decision, so the page is not empty
  if (!selectedDecisionId.value && decisions.length) {
    selectedDecisionId.value = decisions[0].decisionId;
  }
});

// Get selected decision
const selectedDecision = computed(() =>
  userSDGLabelDecisions.value.find(decision => decision.decisionId === selectedDecisionId.value) || null
);
// Watch for changes in selectedDecisionId and fetch the corresponding sdgLabelSummary
watch(selectedDecisionId, async (newDecisionId) => {
  if (newDecisionId && selectedDecision.value) {
    await sdgLabelSummariesStore.fetchSDGLabelSummaryByPublicationId(selectedDecision.value.publicationId);
  }
});

const sdgs = computed(() => {
  if (!sdgLabelSummary.value || !sdgsStore.sdgs.length) return [];

  // Map SDGs and determine their label state
  return sdgsStore.sdgs.map((sdg) => {
    const sdgKey = `sdg${sdg.id}`; // Match SDG key (e.g., sdg1, sdg2)
    return {
      ...sdg,
      label: sdgLabelSummary.value[sdgKey], // 1, 0, or -1
    };
  });
});

// Fetch contributors (annotators & voters)
const getContributors = (decision) => {
  if (!decision) return [];

  const userIds = new Set([
    ...(decision.annotations || []).map(a => a.userId),
    ...(decision.userLabels || []).flatMap(label => (label.votes || []).map(vote => vote.userId)),
    ...(decision.annotations || []).flatMap(annotation => (annotation.votes || []).map(vote => vote.userId))
  ]);

  return usersStore.users.filter(user => userIds.has(user.userId));
};

const getSDGColor = (sdgId: number) => {
  const sdg = sdgsStore.sdgs.find((s) => s.id === sdgId);
  return sdg ? sdg.color : "#A0A0A0"; // Default to gray if SDG not found
};

const getSDGTitle = (sdgId: number) => {
  const sdg = sdgsStore.sdgs.find((s) => s.id === sdgId);
  return sdg ? sdg.shortTitle : "Unknown SDG";
};

const getUserVotedSDG = (userId) => {
  if (!userId) return null;
  const userLabel = userSDGLabelDecisions.value
    .flatMap(decision => decision.userLabels)
    .find(label => label.userId === userId);
  return userLabel?.votedLabel || null;
};

const getUserRank = (userId) => {
  const userRankData = usersStore.users.find((user) => user.userId === userId);
  return userRankData?.rank || { tier: 0, name: "Unranked" };
};

const getUserName = (userId) => {
  const user = usersStore.users.find((user) => user.userId === userId);
  return user ? user.nickname : "Unknown User";
};

const getBorderStyle = (tier) => {
  switch (tier) {
    case 1:
      return "border-double";
    case 2:
      return "border-dashed";
    case 3:
      return "border-solid";
    default:
      return "border-solid";
  }
};

const getUserAvatar = (userId) => {
  const user = usersStore.users.find((user) => user.userId === userId);
  return user ? generateAvatar(user.email) : "https://via.placeholder.com/40";
};

const getSDGIcon = (sdgId: number) => {
  const sdg = sdgsStore.sdgs.find((s) => s.id === sdgId);
  return sdg ? `data:image/svg+xml;base64,${sdg.icon}` : null;
};

const getUserById = (userId: number) => {
  return usersStore.users.find(user => user.userId === userId) || null;
};


const getUserRankForSDG = (userId: number, sdgId: number) => {

  // Ensure rank store is populated
  if (!rankStore.userSDGRanks || rankStore.userSDGRanks.length === 0) {
    return { tier: 0, name: "Unranked" };
  }

  // Find the user's rank data
  const userRankData = rankStore.userSDGRanks.find((u) => u.userId === userId);

  if (!userRankData) {
    return { tier: 0, name: "Unranked" };
  }
  // Find the rank specific to the SDG
  const rank = userRankData.ranks.find((r) => r.sdgGoalId === sdgId);

  if (!rank) {
    return { tier: 0, name: "Unranked" };
  }

  return { tier: rank.tier, name: rank.name };
};

onMounted(async () => {
  await fetchData(); // Ensure all necessary data is fetched before use
});

// Fetch all necessary data before rendering
async function fetchData() {
  try {
    loading.value = true;

    await usersStore.fetchUsers(); // Ensure users are loaded
    await rankStore.fetchSDGRanksForUsers(); // Load user SDG ranks
    labelDecisionsStore.fetchSDGLabelDecisionsForUser(userId.value);

    console.log("📡 Fetched user SDG ranks:", rankStore.userSDGRanks);

  } catch (err) {
    console.error("❌ Error fetching initial data:", err);
    error.value = err.message || "Failed to load data.";
  } finally {
    loading.value = false;
  }
}

</script>

<style scoped>
.decision-item {
  @apply flex w-full items-start gap-2.5 rounded-xl border border-transparent px-2 py-2 text-left transition-colors hover:border-line hover:bg-muted/60;
}
.decision-item.is-active {
  border-color: var(--sdg);
  background: color-mix(in srgb, var(--sdg) 12%, transparent);
}
.decision-item__hex {
  @apply grid h-8 w-9 flex-none place-items-center font-mono text-xs font-bold text-white;
  background: var(--sdg);
}
.decision-item__title {
  @apply text-sm font-medium leading-snug text-fg;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.decision-chip {
  @apply inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm font-semibold text-fg;
  border-color: var(--sdg);
  background: color-mix(in srgb, var(--sdg) 14%, transparent);
}
.sdg-state {
  @apply flex flex-col items-center gap-1;
}
.sdg-state__hex {
  @apply grid h-9 w-10 place-items-center font-mono text-xs font-bold;
}
.sdg-state.is-yes .sdg-state__hex {
  background: var(--sdg);
  color: #fff;
}
.sdg-state.is-open .sdg-state__hex {
  @apply bg-muted text-fg-faint;
}
.sdg-state.is-no .sdg-state__hex {
  @apply bg-hero-red/15 text-hero-red;
}
.entry {
  @apply flex items-start gap-3 rounded-xl border border-line bg-surface-2/70 p-3;
  box-shadow: inset 3px 0 0 var(--sdg);
}
</style>
