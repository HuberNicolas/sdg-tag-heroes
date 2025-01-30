<template>
  <div class="max-w-4xl mx-auto p-4">
    <div v-if="isLoading" class="text-blue-500">Loading...</div>
    <div v-if="error" class="text-red-500">Error: {{ error }}</div>

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
    </div>

    <!-- Scrollable List -->
    <div class="max-h-[600px] overflow-y-auto border rounded p-4">
      <div
        v-for="label in filteredAndSortedUserLabels"
        :key="label.labelId"
        class="mb-6 border-b pb-4"
      >
        <div class="flex items-start gap-4">
          <!-- User Avatar -->
          <img
            v-if="usersStore.users.find(user => user.userId === label.userId)?.email"
            :src="generateAvatar(usersStore.users.find(user => user.userId === label.userId)?.email)"
            alt="User Avatar"
            class="w-10 h-10 rounded-full flex-shrink-0"
          />
          <div v-else class="w-10 h-10 rounded-full bg-gray-300 flex-shrink-0"></div>

          <div class="flex-1">
            <!-- User Nickname and Voted Label -->
            <div class="flex items-center gap-2">
              <p class="font-semibold">
                {{
                  usersStore.users.find(user => user.userId === label.userId)?.nickname || 'Unknown User'
                }}
              </p>
              <div class="flex items-center gap-2">
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
            <p class="text-sm text-gray-700 mt-1">
              <span class="font-medium">Abstract:</span> {{ label.abstractSection || 'None' }}
            </p>

            <!-- User Comment -->
            <p class="text-sm text-gray-700 mt-1">
              <span class="font-medium">Comment:</span> {{ label.comment || 'No comment provided' }}
            </p>

            <!-- Label Date -->
            <p class="text-xs text-gray-500 mt-1">
              <span class="font-medium">Date:</span> {{ formatDate(label.createdAt) }}
            </p>

            <!-- Votes for the Label -->
            <BarVotePlot :width="150" :height="50" :votesData="getLabelVotes(label.labelId)" />
            <div class="flex items-center gap-2 mt-2">
              <button @click="voteLabel(label.labelId, 'positive')" class="text-green-500">
                👍 {{ getLabelVotes(label.labelId).positive }}
              </button>
              <button @click="voteLabel(label.labelId, 'neutral')" class="text-gray-500">
                😐 {{ getLabelVotes(label.labelId).neutral }}
              </button>
              <button @click="voteLabel(label.labelId, 'negative')" class="text-red-500">
                👎 {{ getLabelVotes(label.labelId).negative }}
              </button>
            </div>

            <!-- Toggle Annotations Button -->
            <button
              @click="toggleAnnotations(label.labelId)"
              class="text-blue-500 mt-2"
            >
              {{
                expandedLabels.includes(label.labelId)
                  ? 'Hide Annotations'
                  : 'Show Annotations'
              }}
            </button>

            <!-- Annotations for the User Label -->
            <div
              v-if="expandedLabels.includes(label.labelId)"
              class="mt-4 ml-6"
            >
              <div
                v-for="annotation in label.annotations"
                :key="annotation.annotationId"
                class="mb-4"
              >
                <div class="flex items-start gap-4">
                  <!-- Annotation User Avatar -->
                  <img
                    v-if="annotation.user && annotation.user.email"
                    :src="generateAvatar(annotation.user.email)"
                    alt="Annotation User Avatar"
                    class="w-8 h-8 rounded-full flex-shrink-0"
                  />
                  <div v-else class="w-8 h-8 rounded-full bg-gray-300 flex-shrink-0"></div>

                  <div class="flex-1">
                    <p class="font-medium">
                      Annotation by {{ annotation.user?.email || 'Unknown User' }}
                    </p>
                    <p class="text-sm text-gray-700">{{ annotation.comment }}</p>

                    <!-- Votes for the Annotation -->
                    <div class="flex items-center gap-2 mt-2">
                      <button
                        @click="voteAnnotation(annotation.annotationId, 'positive')"
                        class="text-green-500"
                      >
                        👍 {{ getAnnotationVotes(annotation.annotationId).positive }}
                      </button>
                      <button
                        @click="voteAnnotation(annotation.annotationId, 'negative')"
                        class="text-red-500"
                      >
                        👎 {{ getAnnotationVotes(annotation.annotationId).negative }}
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
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users";
import { useSDGsStore } from "~/stores/sdgs";
import { generateAvatar } from "~/utils/avatar";
import { formatDate } from "~/utils/formatDate";
import { VoteType } from "~/types/enums";
import BarVotePlot from "~/components/plots/BarVotePlot.vue";

const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();
const sdgsStore = useSDGsStore();

const userLabels = computed(() => labelDecisionsStore.userLabels);
const isLoading = computed(() => labelDecisionsStore.isLoading);
const error = computed(() => labelDecisionsStore.error);

// Track expanded labels
const expandedLabels = ref<number[]>([]);
const sortBy = ref("date"); // Default sorting criteria
const filterBy = ref("all"); // Default: Show all labels

// Fetch user labels for a publication on component mount
const route = useRoute();
const publicationId = route.params.publicationId; // 88466

onMounted(async () => {
  await labelDecisionsStore.fetchUserLabelsByPublicationId(publicationId);
  await labelDecisionsStore.fetchSDGLabelDecisionByPublicationId(publicationId);
  await usersStore.fetchUsers(); // Fetch users for avatars
  await sdgsStore.fetchSDGs(); // Fetch SDGs for icons
});

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
  return {
    positive: label.votes.filter((vote) => vote.voteType === VoteType.POSITIVE).length,
    neutral: label.votes.filter((vote) => vote.voteType === VoteType.NEUTRAL).length,
    negative: label.votes.filter((vote) => vote.voteType === VoteType.NEGATIVE).length,
  };
};

// Get votes for an annotation
const getAnnotationVotes = (annotationId: number) => {
  const annotation = userLabels.value
    .flatMap((label) => label.annotations)
    .find((annotation) => annotation.annotationId === annotationId);
  if (!annotation) return { positive: 0, neutral: 0, negative: 0 };
  return {
    positive: annotation.votes.filter((vote) => vote.voteType === VoteType.POSITIVE).length,
    neutral: annotation.votes.filter((vote) => vote.voteType === VoteType.NEUTRAL).length,
    negative: annotation.votes.filter((vote) => vote.voteType === VoteType.NEGATIVE).length,
  };
};

// Vote for a label
const voteLabel = async (labelId: number, voteType: VoteType.POSITIVE | VoteType.NEGATIVE) => {
  // Implement vote logic here
  console.log(`Voted ${voteType} on label ${labelId}`);
};

// Vote for an annotation
const voteAnnotation = async (annotationId: number, voteType: VoteType.POSITIVE | VoteType.NEGATIVE) => {
  // Implement vote logic here
  console.log(`Voted ${voteType} on annotation ${annotationId}`);
};

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


</script>
