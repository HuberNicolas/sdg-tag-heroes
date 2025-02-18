<template>
  <div class="max-w-4xl mx-auto p-4">
    <div v-if="isLoading" class="text-blue-500">Loading...</div>

    <!-- <div v-if="error" class="text-red-500">
      No Label Decision Yet
      Error: {{ error }}
    </div> -->

    <div v-if="error">
      Be the first user to make a comment.
    </div>


    <!-- Sorting Controls -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">User Labels</h2>
      <div class="flex items-center gap-2">
        <label for="sort" class="text-sm font-medium">Sort by:</label>
        <select
          id="sort"
          v-model="sortBy"
          class="p-2 border rounded"
          @change="sortLabels"
        >
          <option value="date">Date</option>
          <option value="nickname">Nickname</option>
          <option value="positiveVotes">Positive Votes</option>
          <option value="negativeVotes">Negative Votes</option>
          <option value="votedLabel">Voted Label</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label for="filter" class="text-sm font-medium">Filter by SDG:</label>
        <select
          id="filter"
          v-model="filterBy"
          class="p-2 border rounded"
        >
          <option value="all">All</option>
          <option v-for="sdg in sdgsStore.sdgs" :key="sdg.id" :value="sdg.id">
            SDG {{ sdg.id }}
          </option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <input id="showAllLabels" type="checkbox" v-model="showAllLabels" class="h-4 w-4" />
        <label for="showAllLabels" class="text-sm font-medium">Show all labels</label>
      </div>
    </div>

    <!-- Scrollable List -->
    <div class="max-h-[600px] overflow-y-auto border rounded p-4">
      <div
        v-for="label in filteredAndSortedUserLabels"
        :key="label.labelId"
        class="mb-6 border-b pb-4"
      >
        <div class="flex items-start gap-4">

          <!-- User Avatar with Rank -->
          <div class="flex flex-col items-center p-4">
            <!-- Check if the user exists (has an email) -->
            <template v-if="usersStore.users.find(user => user.userId === label.userId)?.email">
              <NuxtLink :to="`/users/${label.userId}`" class="flex items-center justify-center">
                <!-- Avatar with Frame -->
                <div
                  v-if="getUserRank(label.userId, label.votedLabel) && getUserRank(label.userId, label.votedLabel).tier !== 0"
                  :style="{ borderColor: sdgsStore.getColorBySDG(label.votedLabel) }"
                  :class="['w-12 h-12 rounded-full border-4 flex items-center justify-center', getBorderStyle(getUserRank(label.userId, label.votedLabel).tier)]"
                >
                  <img
                    :src="generateAvatar(usersStore.users.find(user => user.userId === label.userId)?.email)"
                    alt="User Avatar"
                    class="w-10 h-10 rounded-full"
                  />
                </div>
                <!-- Plain Avatar if no rank -->
                <template v-else>
                  <img
                    :src="generateAvatar(usersStore.users.find(user => user.userId === label.userId)?.email)"
                    alt="User Avatar"
                    class="w-12 h-12 rounded-full"
                  />
                </template>
              </NuxtLink>
            </template>
            <!-- Fallback if user data is missing -->
            <template v-else>
              <div class="w-12 h-12 rounded-full bg-gray-300"></div>
            </template>

            <!-- Rank Info Card -->
            <div v-if="getUserRank(label.userId, label.votedLabel)"
                 class="mt-2 bg-white rounded-lg shadow p-2 w-full text-center border">
              <p>Rank</p>
              <Icon
                v-if="getUserRank(label.userId, label.votedLabel).tier === 1"
                name="line-md:chevron-up"
                :style="{ color: sdgsStore.getColorBySDG(label.votedLabel) }"
                class="w-5 h-5 mx-auto"
              />
              <Icon
                v-else-if="getUserRank(label.userId, label.votedLabel).tier === 2"
                name="line-md:chevron-double-up"
                :style="{ color: sdgsStore.getColorBySDG(label.votedLabel) }"
                class="w-5 h-5 mx-auto"
              />
              <Icon
                v-else-if="getUserRank(label.userId, label.votedLabel).tier === 3"
                name="line-md:chevron-triple-up"
                :style="{ color: sdgsStore.getColorBySDG(label.votedLabel) }"
                class="w-5 h-5 mx-auto"
              />
              <Icon
                v-else
                name="line-md:minus"
                class="text-gray-400 w-5 h-5 mx-auto"
              />
            </div>
          </div>
          <div class="flex-1 bg-white rounded-tr-lg rounded-br-lg rounded-bl-lg p-4">

            <!-- User Nickname and Voted Label -->
            <div class="flex items-center gap-2">
              <p class="font-semibold">
                {{
                  usersStore.users.find(user => user.userId === label.userId)?.nickname || "Unknown User"
                }}
              </p>
              <!-- Rank title Section -->
              <p class="text-sm border-gray-400 mt-1">
                <span class="text-sm border-gray-400 mt-1">{{ getUserRank(label.userId, label.votedLabel)?.name || ""
                  }}</span>
              </p>
              <div class="flex items-center gap-2 ml-auto">
                <img
                  v-if="getSDGIcon(label.votedLabel)"
                  :src="getSDGIcon(label.votedLabel)"
                  alt="SDG Icon"
                  class="w-6 h-6 rounded-full"
                />
                <span>SDG {{ label.votedLabel }}</span>
              </div>
            </div>

            <!-- Abstract Section -->
            <p class="text-sm border-gray-400 mt-1">
              <span class="font-medium">Abstract:</span> {{ label.abstractSection || "None" }}
            </p>

            <!-- User Comment -->
            <p class="text-sm text-gray-700 mt-1">
              <span class="font-medium">Comment:</span> {{ label.comment || "No comment provided" }}
            </p>

            <!-- Label Date -->
            <p class="text-xs text-gray-500 mt-1">
              <span class="font-medium">Date:</span> {{ formatDate(label.createdAt) }}
            </p>

            <!-- Votes for the Label -->
            <div class="flex items-center gap-4 mt-2 h-[50px]">
              <p class="font-semibold text-gray-700">User Votes</p>
              <!-- Vote Plot -->
              <BarVotePlot :width="150" :height="50" :votesData="getLabelVotes(label.labelId)" />

              <!-- Vote Buttons -->
              <div class="flex items-center gap-2 mt-2">
                <!-- Positive Vote Button -->
                <button
                  @click="voteLabel(label.labelId, VoteType.POSITIVE)"
                  class="flex items-center gap-1 text-blue-500 hover:text-blue-700"
                  aria-label="Vote Positive"
                >
                  <Icon name="mdi-thumb-up-outline" class="w-5 h-5" />
                  <span>{{ getLabelVotes(label.labelId).positive }}</span>
                </button>

                <!-- Neutral Vote Button -->
                <button
                  @click="voteLabel(label.labelId, VoteType.NEUTRAL)"
                  class="flex items-center gap-1 text-gray-500 hover:text-gray-700"
                  aria-label="Vote Neutral"
                >
                  <Icon name="mdi-emoticon-neutral-outline" class="w-5 h-5" />
                  <span>{{ getLabelVotes(label.labelId).neutral }}</span>
                </button>

                <!-- Negative Vote Button -->
                <button
                  @click="voteLabel(label.labelId, VoteType.NEGATIVE)"
                  class="flex items-center gap-1 text-red-500 hover:text-red-700"
                  aria-label="Vote Negative"
                >
                  <Icon name="mdi-thumb-down-outline" class="w-5 h-5" />
                  <span>{{ getLabelVotes(label.labelId).negative }}</span>
                </button>
              </div>
            </div>

            <!-- Toggle Annotations Button -->
            <button
              @click="toggleAnnotations(label.labelId)"
              class="text-blue-500 mt-2"
            >
              {{
                expandedLabels.includes(label.labelId)
                  ? "Hide Annotations"
                  : "Show Annotations"
              }}
            </button>

            <!-- Annotations for the User Label -->
            <!-- Annotations for the User Label -->
            <div v-if="expandedLabels.includes(label.labelId)" class="mt-4 ml-6">
              <div
                v-for="annotation in label.annotations"
                :key="annotation.annotationId"
                class="mb-4 border-b pb-4"
              >
                <div class="flex items-start gap-4">
                  <!-- Annotation User Avatar with Rank -->
                  <div class="flex flex-col items-center p-2">
                    <template v-if="annotation.user?.email">
                      <!-- Avatar with Rank Border -->
                      <div
                        v-if="annotation.user && getUserRank(annotation.user?.userId, label.votedLabel)?.tier !== 0"
                        :style="{ borderColor: sdgsStore.getColorBySDG(label.votedLabel) }"
                        :class="['w-8 h-8 rounded-full border-4 flex items-center justify-center', getBorderStyle(getUserRank(annotation.user?.userId, label.votedLabel)?.tier)]"
                      >
                        <img
                          :src="generateAvatar(annotation.user.email)"
                          alt="Annotation User Avatar"
                          class="w-7 h-7 rounded-full"
                        />
                      </div>
                      <!-- Plain Avatar if no rank -->
                      <template v-else>
                        <img
                          :src="generateAvatar(annotation.user.email)"
                          alt="Annotation User Avatar"
                          class="w-8 h-8 rounded-full"
                        />
                      </template>
                    </template>
                    <!-- Fallback if user data is missing -->
                    <template v-else>
                      <div class="w-8 h-8 rounded-full bg-gray-300"></div>
                    </template>

                    <!-- Rank Info Card -->
                    <div v-if="annotation.user && getUserRank(annotation.user?.userId, label.votedLabel)"
                         class="mt-2 bg-white rounded-lg shadow p-2 w-full text-center border">
                      <p>Rank</p>
                      <Icon
                        v-if="getUserRank(annotation.user?.userId, label.votedLabel)?.tier === 1"
                        name="line-md:chevron-up"
                        :style="{ color: sdgsStore.getColorBySDG(label.votedLabel) }"
                        class="w-4 h-4 mx-auto"
                      />
                      <Icon
                        v-else-if="getUserRank(annotation.user?.userId, label.votedLabel)?.tier === 2"
                        name="line-md:chevron-double-up"
                        :style="{ color: sdgsStore.getColorBySDG(label.votedLabel) }"
                        class="w-4 h-4 mx-auto"
                      />
                      <Icon
                        v-else-if="getUserRank(annotation.user?.userId, label.votedLabel)?.tier === 3"
                        name="line-md:chevron-triple-up"
                        :style="{ color: sdgsStore.getColorBySDG(label.votedLabel) }"
                        class="w-4 h-4 mx-auto"
                      />
                      <Icon
                        v-else
                        name="line-md:minus"
                        class="text-gray-400 w-4 h-4 mx-auto"
                      />
                    </div>
                  </div>

                  <!-- Annotation Content -->
                  <div class="flex-1 bg-white rounded-tr-lg rounded-br-lg rounded-bl-lg p-4">
                    <!-- User Name and Rank -->
                    <div class="flex items-center gap-2">
                      <p class="font-semibold">
                        {{ annotation.user?.nickname || "Unknown User" }}
                      </p>
                      <p class="text-sm border-gray-400 mt-1">
            <span class="text-sm border-gray-400 mt-1">
              {{ annotation.user ? getUserRank(annotation.user.userId, label.votedLabel)?.name || "" : "" }}
            </span>
                      </p>
                    </div>

                    <!-- Annotation Comment -->
                    <p class="text-sm text-gray-700 mt-1">
                      <span class="font-medium">Comment:</span> {{ annotation.comment }}
                    </p>

                    <!-- Annotation Date -->
                    <p class="text-xs text-gray-500 mt-1">
                      <span class="font-medium">Date:</span> {{ formatDate(annotation.createdAt) }}
                    </p>

                    <!-- Votes for the Annotation -->
                    <div class="flex items-center gap-4 mt-2 h-[40px]">
                      <p class="font-semibold text-gray-700">User Votes</p>
                      <!-- Vote Plot -->
                      <BarVotePlot :width="120" :height="40" :votesData="getAnnotationVotes(annotation.annotationId)" />

                      <!-- Vote Buttons -->
                      <div class="flex items-center gap-2 mt-2">
                        <!-- Positive Vote Button -->
                        <button
                          @click="voteAnnotation(annotation.annotationId, VoteType.POSITIVE)"
                          class="flex items-center gap-1 text-blue-500 hover:text-blue-700"
                          aria-label="Vote Positive"
                        >
                          <Icon name="mdi-thumb-up-outline" class="w-4 h-4" />
                          <span>{{ getAnnotationVotes(annotation.annotationId).positive }}</span>
                        </button>

                        <!-- Neutral Vote Button -->
                        <button
                          @click="voteAnnotation(annotation.annotationId, VoteType.NEUTRAL)"
                          class="flex items-center gap-1 text-gray-500 hover:text-gray-700"
                          aria-label="Vote Neutral"
                        >
                          <Icon name="mdi-emoticon-neutral-outline" class="w-4 h-4" />
                          <span>{{ getAnnotationVotes(annotation.annotationId).neutral }}</span>
                        </button>

                        <!-- Negative Vote Button -->
                        <button
                          @click="voteAnnotation(annotation.annotationId, VoteType.NEGATIVE)"
                          class="flex items-center gap-1 text-red-500 hover:text-red-700"
                          aria-label="Vote Negative"
                        >
                          <Icon name="mdi-thumb-down-outline" class="w-4 h-4" />
                          <span>{{ getAnnotationVotes(annotation.annotationId).negative }}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users";
import { useSDGsStore } from "~/stores/sdgs";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { generateAvatar } from "~/utils/avatar";
import { formatDate } from "~/utils/formatDate";
import { VoteType } from "~/types/enums";
import BarVotePlot from "~/components/plots/BarVotePlot.vue";
import type { VoteSchemaFull } from "~/types/vote";
import useVotes from "~/composables/useVotes";

const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();
const sdgsStore = useSDGsStore();
const rankStore = useSDGRanksStore();

const userLabels = computed(() => {
  if (showAllLabels.value) {
    return labelDecisionsStore.userLabels; // Show all labels
  }

  // Show only the latest label per user
  const latestLabels = new Map<number, any>();
  labelDecisionsStore.userLabels.forEach((label) => {
    if (
      !latestLabels.has(label.userId) ||
      new Date(label.createdAt) > new Date(latestLabels.get(label.userId).createdAt)
    ) {
      latestLabels.set(label.userId, label);
    }
  });

  return Array.from(latestLabels.values());
});


const isLoading = computed(() => labelDecisionsStore.isLoading);
const error = computed(() => labelDecisionsStore.error);

// Track expanded labels
const expandedLabels = ref<number[]>([]);
const sortBy = ref("date"); // Default sorting criteria
const filterBy = ref("all"); // Default: Show all labels
const showAllLabels = ref(false);

// Fetch user labels for a publication on component mount
const route = useRoute();
const publicationId = route.params.publicationId; // 88466

// Toggle annotations visibility
const toggleAnnotations = (labelId: number) => {
  if (expandedLabels.value.includes(labelId)) {
    expandedLabels.value = expandedLabels.value.filter((id) => id !== labelId);
  } else {
    expandedLabels.value.push(labelId);
  }
};

// Get SDG Icon
const getSDGIcon = (sdgId: number) => {
  const sdg = sdgsStore.sdgs.find((sdg) => sdg.id === sdgId);
  return sdg ? `data:image/svg+xml;base64,${sdg.icon}` : null;
};

// Get votes for a label
const getLabelVotes = (labelId: number) => {
  const label = userLabels.value.find((label) => label.labelId === labelId);
  if (!label) return { positive: 0, neutral: 0, negative: 0 };

  // Use a Map to ensure only the latest vote per user is counted
  const latestVotes = new Map<number, string>();

  label.votes.forEach((vote) => {
    latestVotes.set(vote.userId, vote.voteType);
  });

  return {
    positive: Array.from(latestVotes.values()).filter(vote => vote === VoteType.POSITIVE).length,
    neutral: Array.from(latestVotes.values()).filter(vote => vote === VoteType.NEUTRAL).length,
    negative: Array.from(latestVotes.values()).filter(vote => vote === VoteType.NEGATIVE).length
  };
};


// Get votes for an annotation
const getAnnotationVotes = (annotationId: number) => {
  console.log("getAnnotationVotes", annotationId);
  const annotation = userLabels.value
    .flatMap((label) => label.annotations)
    .find((annotation) => annotation.annotationId === annotationId);
  if (!annotation) return { positive: 0, neutral: 0, negative: 0 };
  const dict =  {
    positive: annotation.votes.filter((vote) => vote.voteType === VoteType.POSITIVE).length,
    neutral: annotation.votes.filter((vote) => vote.voteType === VoteType.NEUTRAL).length,
    negative: annotation.votes.filter((vote) => vote.voteType === VoteType.NEGATIVE).length
  };
  console.log(dict);
  return dict
};

// Vote for a label
async function voteLabel(sdgUserLabelId: number, voteType: VoteType): Promise<VoteSchemaFull> {
  const userId = usersStore.user.userId;
  const score = 1
  const {createVote} = useVotes();
  console.log(`Voted ${voteType} on label ${sdgUserLabelId}`);
  try {
    const voteData = {
      user_id: userId,
      sdg_user_label_id: sdgUserLabelId,
      vote_type: voteType,
      score: score,
    };
    return await createVote(voteData);
  } catch (error) {
    throw new Error(`Failed to vote on label: ${error}`);
  }
}

// Vote for an annotation
async function voteAnnotation(annotationId: number, voteType: VoteType): Promise<VoteSchemaFull> {
  const userId = usersStore.user.userId;
  const score = 1
  const {createVote} = useVotes();
  console.log(`Voted ${voteType} on annotation ${annotationId}`);
  try {
    const voteData = {
      user_id: userId,
      annotation_id: annotationId,
      vote_type: voteType,
      score: score,
    };
    return await createVote(voteData);
  } catch (error) {
    throw new Error(`Failed to vote on label: ${error}`);
  }
}

const filteredAndSortedUserLabels = computed(() => {
  let filteredLabels = userLabels.value;

  // Apply filtering based on selected criteria
  if (filterBy.value !== "all") {
    filteredLabels = filteredLabels.filter((label) => label.votedLabel === Number(filterBy.value));
  }

  // Apply sorting after filtering
  return [...filteredLabels].sort((a, b) => {
    switch (sortBy.value) {
      case "nickname":
        const nicknameA =
          usersStore.users.find((user) => user.userId === a.userId)?.nickname ||
          "";
        const nicknameB =
          usersStore.users.find((user) => user.userId === b.userId)?.nickname ||
          "";
        return nicknameA.localeCompare(nicknameB);

      case "positiveVotes":
        return (
          getLabelVotes(b.labelId).positive - getLabelVotes(a.labelId).positive
        );

      case "negativeVotes":
        return (
          getLabelVotes(b.labelId).negative - getLabelVotes(a.labelId).negative
        );

      case "votedLabel":
        return a.votedLabel - b.votedLabel;

      case "date":
      default:
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    }
  });
});

// Helper to get a user’s rank for a given SDG (using the label’s votedLabel)
const getUserRank = (userId: number, sdgId: number) => {
  const userRankData = rankStore.userSDGRanks.find((u) => u.userId === userId);
  if (!userRankData) return null;
  return userRankData.ranks.find((r) => r.sdgGoalId === sdgId) || null;
};

// Function to return a border style based on rank tier
const getBorderStyle = (tier: number) => {
  switch (tier) {
    case 1:
      return "border-double"; // or any class you use for tier 1
    case 2:
      return "border-dashed"; // for tier 2
    case 3:
      return "border-solid";  // for tier 3
    default:
      return ""; // No extra style if no rank or tier 0
  }
};

</script>
