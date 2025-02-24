<template>
  <div>
    <div class="frame-title"><b>Browse</b> Community Annotations: Read & Engage with Shared Insights</div>
    <div v-if="isLoading" class="text-gray-500">Loading...</div>

    <div v-if="error">Be the first user to make an annotation.</div>

    <!-- Sorting Controls -->
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 p-4 border rounded-md shadow-sm">
      <h2 class="text-xl font-semibold">Community Annotations</h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 w-full md:w-auto">
        <!-- Sort By -->
        <div class="flex flex-wrap items-center gap-x-2">
          <label for="sort" class="text-sm font-medium">Sort by:</label>
          <select id="sort" v-model="sortBy" class="p-2 border rounded w-auto">
            <option value="date">Date</option>
            <option value="nickname">Nickname</option>
            <option value="positiveVotes">Positive Votes</option>
            <option value="negativeVotes">Negative Votes</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Scrollable List -->
    <div class="max-h-[600px] overflow-y-auto border rounded p-4">
      <div v-for="annotation in sortedAnnotations" :key="annotation.annotationId"
           class="mb-2 border-2 border-gray-600 bg-gray-200 rounded-lg shadow-xl p-3">
      <div class="flex items-start gap-2">
          <!-- User Avatar with Rank -->
          <div class="flex flex-col items-center p-4">
            <template v-if="usersStore.users.find(user => user.userId === annotation.userId)?.email">
              <NuxtLink :to="`/users/${annotation.userId}`" class="flex items-center justify-center">
                <img :src="generateAvatar(usersStore.users.find(user => user.userId === annotation.userId)?.email)" alt="User Avatar" class="w-12 h-12 rounded-full" />
              </NuxtLink>
            </template>
            <template v-else>
              <div class="w-12 h-12 rounded-full bg-gray-300"></div>
            </template>
          </div>

          <div class="flex-1 bg-white rounded-tr-lg rounded-br-lg rounded-bl-lg p-4">
            <!-- User Nickname and Annotation -->
            <div class="flex items-center gap-2">
              <p class="font-semibold">
                {{ usersStore.users.find(user => user.userId === annotation.userId)?.nickname || "Unknown User" }}
              </p>
            </div>

            <!-- Annotation Comment -->
            <p class="text-sm text-gray-700 mt-1">
              <span class="font-medium">Comment:</span> {{ annotation.comment || "No comment provided" }}
            </p>

            <!-- Annotation Date -->
            <p class="text-xs text-gray-500 mt-1">
              <span class="font-medium">Date:</span> {{ formatDate(annotation.createdAt) }}
            </p>

            <!-- Votes for the Annotation -->
            <div class="flex items-center gap-2 mt-2 h-[50px]">
              <p class="font-semibold text-gray-700">Community Votes</p>

              <!-- Vote Buttons -->
              <div class="flex items-center gap-2 mt-2">
                <!-- Negative Vote Button -->
                <button @click="voteAnnotation(annotation.annotationId, VoteType.NEGATIVE)" class="flex items-center gap-1 text-gray-400 hover:text-gray-600" aria-label="Vote Negative">
                  <Icon name="mdi-thumb-down-outline" class="w-5 h-5" />
                  <span class="text-gray-400">{{ getAnnotationVotes(annotation.annotationId).negative }}</span>
                </button>

                <!-- Vote Plot -->
                <BarVotePlot :width="350" :height="80" :votesData="getAnnotationVotes(annotation.annotationId)" />

                <!-- Positive Vote Button -->
                <button @click="voteAnnotation(annotation.annotationId, VoteType.POSITIVE)" class="flex items-center gap-1 text-gray-700 hover:text-gray-900" aria-label="Vote Positive">
                  <Icon name="mdi-thumb-up-outline" class="w-5 h-5" />
                  <span class="text-gray-700">{{ getAnnotationVotes(annotation.annotationId).positive }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users";
import { generateAvatar } from "~/utils/avatar";
import { formatDate } from "~/utils/formatDate";
import { VoteType } from "~/types/enums";
import type { VoteSchemaFull } from "~/types/vote";
import BarVotePlot from "~/components/plots/BarVotePlot.vue";

const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();
const isLoading = computed(() => labelDecisionsStore.isLoading);
const error = computed(() => labelDecisionsStore.error);
const sortBy = ref("date"); // Default sorting option

const sortedAnnotations = computed(() => {
  const annotations = [...labelDecisionsStore.annotations];

  return annotations.sort((a, b) => {
    if (sortBy.value === "date") {
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    } else if (sortBy.value === "nickname") {
      const nicknameA = usersStore.users.find(user => user.userId === a.userId)?.nickname || "";
      const nicknameB = usersStore.users.find(user => user.userId === b.userId)?.nickname || "";
      return nicknameA.localeCompare(nicknameB);
    } else if (sortBy.value === "positiveVotes") {
      return getAnnotationVotes(b.annotationId).positive - getAnnotationVotes(a.annotationId).positive;
    } else if (sortBy.value === "negativeVotes") {
      return getAnnotationVotes(b.annotationId).negative - getAnnotationVotes(a.annotationId).negative;
    }
    return 0;
  });
});

const route = useRoute();
const publicationId = computed(() => route.params.publicationId);

onMounted(async () => {
  await labelDecisionsStore.fetchSDGLabelDecisionByPublicationId(publicationId.value);
  if (labelDecisionsStore.selectedSDGLabelDecision) {
    await labelDecisionsStore.fetchAnnotationsByDecisionId(labelDecisionsStore.selectedSDGLabelDecision.decisionId);
  }
  await usersStore.fetchUsers();
});

const getAnnotationVotes = (annotationId: number) => {
  const annotation = labelDecisionsStore.annotations.find(annotation => annotation.annotationId === annotationId);
  if (!annotation) return { positive: 0, negative: 0 };
  return {
    positive: annotation.votes.filter(vote => vote.voteType === VoteType.POSITIVE).length,
    negative: annotation.votes.filter(vote => vote.voteType === VoteType.NEGATIVE).length,
  };
};

async function voteAnnotation(annotationId: number, voteType: VoteType): Promise<VoteSchemaFull> {
  const userId = usersStore.user.userId;
  const score = 1;
  const { createVote } = useVotes();
  console.log(`Voted ${voteType} on annotation ${annotationId}`);
  try {
    const voteData = { user_id: userId, annotation_id: annotationId, vote_type: voteType, score: score };
    return await createVote(voteData);
  } catch (error) {
    throw new Error(`Failed to vote on annotation: ${error}`);
  }
}

</script>
