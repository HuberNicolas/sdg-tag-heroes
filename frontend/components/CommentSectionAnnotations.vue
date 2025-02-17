<template>
  <div class="max-w-4xl mx-auto p-4">
    <div v-if="isLoading" class="text-blue-500">Loading...</div>


    <!-- <div v-if="error" class="text-red-500">
      No Annotations Yet
      Error: {{ error }}
    </div>
    -->


    <div v-if="error">
      Be the first user to make an annotation.
    </div>


    <!-- Annotations List -->
    <div class="max-h-[600px] overflow-y-auto border rounded p-4">
      <div
        v-for="annotation in sortedAnnotations"
        :key="annotation.annotationId"
        class="mb-6 border-b pb-4"
      >
        <div class="flex items-start gap-4">
          <!-- User Avatar -->
          <img
            v-if="usersStore.users.find(user => user.userId === annotation.userId)?.email"
            :src="generateAvatar(usersStore.users.find(user => user.userId === annotation.userId)?.email)"
            alt="User Avatar"
            class="w-10 h-10 rounded-full flex-shrink-0"
          />
          <div v-else class="w-10 h-10 rounded-full bg-gray-300 flex-shrink-0"></div>

          <div class="flex-1">
            <!-- User Nickname -->
            <p class="font-semibold">
              {{
                usersStore.users.find(user => user.userId === annotation.userId)?.nickname || 'Unknown User'
              }}
            </p>

            <!-- Annotation Comment -->
            <p class="text-sm text-gray-700 mt-1">
              <span class="font-medium">Comment:</span> {{ annotation.comment || 'No comment provided' }}
            </p>

            <!-- Annotation Date -->
            <p class="text-xs text-gray-500 mt-1">
              <span class="font-medium">Date:</span> {{ formatDate(annotation.createdAt) }}
            </p>

            <!-- Votes for the Annotation -->
            <div class="flex items-center gap-2 mt-2">
              <button
                @click="voteAnnotation(annotation.annotationId, VoteType.POSITIVE)"
                class="flex items-center gap-1 text-blue-500 hover:text-blue-700"
                aria-label="Vote Positive"
              >
                <Icon name="mdi-thumb-up-outline" class="w-4 h-4" />
                <span>{{ getAnnotationVotes(annotation.annotationId).positive }}</span>
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
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users";
import { generateAvatar } from "~/utils/avatar";
import { formatDate } from "~/utils/formatDate";
import { VoteType } from "~/types/enums";
import type { VoteSchemaFull } from "~/types/vote";

const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();
const isLoading = computed(() => labelDecisionsStore.isLoading);
const error = computed(() => labelDecisionsStore.error);

const sortedAnnotations = computed(() => {
  return [...labelDecisionsStore.annotations].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );
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
  const annotation = labelDecisionsStore.annotations.find(
    (annotation) => annotation.annotationId === annotationId
  );
  if (!annotation) return { positive: 0, negative: 0 };
  return {
    positive: annotation.votes.filter((vote) => vote.voteType === VoteType.POSITIVE).length,
    negative: annotation.votes.filter((vote) => vote.voteType === VoteType.NEGATIVE).length,
  };
};

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
</script>
