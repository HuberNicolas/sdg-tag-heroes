<template>
  <div class="flex h-screen">
    <!-- Sidebar: List of Label Decisions -->
    <div class="w-1/4 bg-gray-100 p-4 overflow-y-auto">
      <h2 class="text-lg font-semibold mb-3">Label Decisions</h2>
      <ul>
        <li
          v-for="decision in userSDGLabelDecisions"
          :key="decision.decisionId"
          class="p-2 mb-2 cursor-pointer border rounded bg-white hover:bg-gray-200"
          :class="{ 'bg-blue-200': decision.decisionId === selectedDecisionId }"
          @click="selectedDecisionId = decision.decisionId"
        >
          <strong>Decision ID:</strong> {{ decision.decisionId }}<br />
          <strong>Publication:</strong> {{ decision.publicationId }}
        </li>
      </ul>
    </div>

    <!-- Main Content: Label Decision Details -->
    <div class="w-3/4 p-4 overflow-y-auto">
      <div v-if="selectedDecision">
        <h2 class="text-xl font-semibold">Label Decision: {{ selectedDecision.decisionId }}</h2>

        <!-- Contributors Section -->
        <div class="flex items-center mb-4">
          <h3 class="text-md font-semibold mr-2">Tag Heroes:</h3>
          <div class="flex -space-x-2">
            <NuxtLink
              v-for="user in getContributors(selectedDecision)"
              :key="user.userId"
              :to="`/users/${user.userId}`"
              class="relative group"
            >
              <div
                :style="{ borderColor: getSDGColor(getUserVotedSDG(user.userId)) }"
                :class="['w-12 h-12 rounded-full border-4 flex items-center justify-center', getBorderStyle(getUserRank(user.userId)?.tier)]"
              >
                <img
                  :src="generateAvatar(user.email)"
                  class="w-10 h-10 rounded-full"
                  :alt="`Avatar of ${user.name}`"
                />
              </div>
              <span
                class="absolute left-1/2 transform -translate-x-1/2 mt-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded px-2 py-1">
                {{ getSDGTitle(getUserVotedSDG(user.userId)) }} | Rank: {{ getUserRank(user.userId)?.name || "Unranked"
                }}
              </span>
            </NuxtLink>
          </div>
        </div>

        <!-- Expandable Sections -->
        <div class="space-y-4">
          <!-- User Labels -->
          <details class="border p-3 rounded">
            <summary class="cursor-pointer text-md font-semibold">User Labels</summary>
            <ul class="mt-2">
              <li
                v-for="label in selectedDecision.userLabels"
                :key="label.labelId"
                class="p-2 border-b"
              >

                <!-- <strong>Label ID:</strong> {{ label.labelId }}<br /> -->
                <strong>User</strong> {{ getUserName(label.userId) }}<br />
                <div class="flex items-center space-x-2">
                  <strong>Voted Label:</strong>
                  <img
                    v-if="getSDGIcon(label.votedLabel)"
                    :src="getSDGIcon(label.votedLabel)"
                    :alt="`SDG ${label.votedLabel} Icon`"
                    class="w-6 h-6 object-contain"
                  />
                  <span>{{ label.votedLabel }}</span>
                </div>

                <!-- Rank Information -->
                <div class="flex items-center space-x-4 mt-2">
                  <!-- Avatar with Frame -->
                  <div class="relative flex items-center justify-center p-2">
                    <!-- Inner Frame with SDG Color Border -->
                    <div
                      v-if="getUserRankForSDG(label.userId, label.votedLabel)?.tier !== 0"
                      :style="{ borderColor: getSDGColor(label.votedLabel) }"
                      :class="[
        'w-16 h-16 rounded-full flex items-center justify-center border-4',
        getBorderStyle(getUserRankForSDG(label.userId, label.votedLabel)?.tier)
      ]"
                    >
                      <!-- Avatar Inside the Frame -->
                      <div class="w-12 h-12 rounded-full overflow-hidden">
                        <img :src="generateAvatar(getUserById(label.userId)?.email)" alt="User Avatar" class="w-full h-full" />
                      </div>
                    </div>

                    <!-- Direct Avatar (No Frame) if Tier is 0 -->
                    <div v-else class="w-12 h-12 rounded-full overflow-hidden">
                      <img :src="generateAvatar(getUserById(label.userId)?.email)" alt="User Avatar" class="w-full h-full" />
                    </div>
                  </div>

                  <span class="text-gray-600 font-semibold">Rank:</span>

                  <!-- Rank Tier -->
                  <span class="px-2 py-1 rounded-lg text-white text-sm font-semibold"
                        :style="{ backgroundColor: getSDGColor(label.votedLabel) }">
    {{ getUserRankForSDG(label.userId, label.votedLabel)?.tier || "-" }}
  </span>

                  <!-- Rank Symbol -->
                  <Icon
                    v-if="getUserRankForSDG(label.userId, label.votedLabel)?.tier === 1"
                    name="line-md:chevron-up"
                    class="w-6 h-6"
                    :style="{ color: getSDGColor(label.votedLabel) }"
                  />
                  <Icon
                    v-else-if="getUserRankForSDG(label.userId, label.votedLabel)?.tier === 2"
                    name="line-md:chevron-double-up"
                    class="w-6 h-6"
                    :style="{ color: getSDGColor(label.votedLabel) }"
                  />
                  <Icon
                    v-else-if="getUserRankForSDG(label.userId, label.votedLabel)?.tier === 3"
                    name="line-md:chevron-triple-up"
                    class="w-6 h-6"
                    :style="{ color: getSDGColor(label.votedLabel) }"
                  />
                  <Icon v-else name="line-md:minus" class="text-gray-400 w-6 h-6" />

                  <!-- Rank Title -->
                  <span class="px-3 py-1 rounded-lg text-white text-sm font-semibold"
                        v-if="getUserRankForSDG(label.userId, label.votedLabel)"
                        :style="{ backgroundColor: getSDGColor(label.votedLabel) }">
    {{ getUserRankForSDG(label.userId, label.votedLabel).name }}
  </span>
                  <span v-else class="text-gray-400">No Rank</span>
                </div>


                <p class="text-gray-600">{{ label.comment }}</p>


                <!-- Votes for User Label -->
                <!--
<details class="border p-2 rounded mt-2">
  <summary class="cursor-pointer font-semibold">Votes</summary>
  <ul>
    <li
      v-for="vote in label.votes"
      :key="vote.voteId"
      class="p-2 border-b flex items-center space-x-3"
    >
      <div
        :style="{ borderColor: getSDGColor(getUserVotedSDG(vote.userId)) }"
        :class="['w-10 h-10 rounded-full border-4 flex items-center justify-center', getBorderStyle(getUserRank(vote.userId)?.tier)]"
      >
        <img
          :src="getUserAvatar(vote.userId)"
          class="w-8 h-8 rounded-full"
          :alt="getUserName(vote.userId)"
        />
      </div>
      <span><strong>{{ getUserName(vote.userId) }}</strong></span>
      <span>Type: {{ vote.vote_type }}</span>
      <span>Score: {{ vote.score }}</span>
    </li>
  </ul>
</details>
-->
              </li>
            </ul>
          </details>

          <!-- Annotations -->
          <details class="border p-3 rounded">
            <summary class="cursor-pointer text-md font-semibold">Annotations</summary>
            <ul class="mt-2">
              <li
                v-for="annotation in selectedDecision.annotations"
                :key="annotation.annotationId"
                class="p-2 border-b flex items-center space-x-3"
              >
                <div
                  :style="{ borderColor: getSDGColor(getUserVotedSDG(annotation.userId)) }"
                  :class="['w-10 h-10 rounded-full border-4 flex items-center justify-center', getBorderStyle(getUserRank(annotation.userId)?.tier)]"
                >
                  <img
                    :src="getUserAvatar(annotation.userId)"
                    class="w-8 h-8 rounded-full"
                    :alt="getUserName(annotation.userId)"
                  />
                </div>
                <span><strong>{{ getUserName(annotation.userId) }}</strong></span>
                <span>Score: {{ annotation.labelerScore }}</span>
                <p class="text-gray-600">{{ annotation.comment }}</p>
              </li>
            </ul>
          </details>
        </div>
      </div>

      <p v-else class="text-center text-gray-500">Select a label decision to view details.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useUsersStore } from "~/stores/users";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";
import { generateAvatar } from "~/utils/avatar";
import { useSDGRanksStore } from "~/stores/sdgRanks";


// Router
const route = useRoute();
const userId = computed(() => Number(route.params.id));

// Stores
const usersStore = useUsersStore();
const labelDecisionsStore = useLabelDecisionsStore();
const sdgsStore = useSDGsStore();
const rankStore = useSDGRanksStore();

const loading = ref(true);
const error = ref<string | null>(null);

// Store data
const userSDGLabelDecisions = computed(() => labelDecisionsStore.userSDGLabelDecisions);
const selectedDecisionId = ref<number | null>(null);

// Get selected decision
const selectedDecision = computed(() =>
  userSDGLabelDecisions.value.find(decision => decision.decisionId === selectedDecisionId.value) || null
);

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
