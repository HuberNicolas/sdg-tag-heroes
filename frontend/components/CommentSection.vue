<template>
  <div class="max-w-4xl mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Publication Comments</h1>

    <div v-if="isLoading" class="text-blue-500">Loading...</div>
    <div v-if="error" class="text-red-500">Error: {{ error }}</div>

    <!-- SDG User Labels -->
    <div v-for="label in userLabels" :key="label.labelId" class="mb-6 border-b pb-4">
      <div class="flex items-start gap-4">
        <!-- User Avatar -->
        <img
          v-if="label.userId && label.userId.email"
          :src="generateAvatar(label.userId.email)"
          alt="User Avatar"
          class="w-10 h-10 rounded-full flex-shrink-0"
        />
        <div v-else class="w-10 h-10 rounded-full bg-gray-300 flex-shrink-0"></div>

        <div class="flex-1">
          <!-- User Nickname and Voted Label -->
          <div class="flex items-center gap-2">
            <p class="font-semibold">{{ label.userId?.nickname || 'Unknown User' }}</p>
            <div class="flex items-center gap-2">
              <!-- SDG Icon -->
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
            <span class="font-medium">Date:</span> {{ label.createdAt }}
          </p>

          <!-- Annotations for the User Label -->
          <div v-for="annotation in label.annotations" :key="annotation.annotationId" class="mt-4 ml-6">
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
                <p class="font-medium">Annotation by {{ annotation.user?.email || 'Unknown User' }}</p>
                <p class="text-sm text-gray-700">{{ annotation.comment }}</p>

                <!-- Votes for the Annotation -->
                <ul class="mt-2 ml-4">
                  <li
                    v-for="vote in annotation.votes"
                    :key="vote.voteId"
                    class="text-sm text-gray-600"
                  >
                    User {{ vote.user?.email || 'Unknown User' }} voted {{ vote.voteType }} with score {{ vote.score }}
                  </li>
                </ul>
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

const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();
const sdgsStore = useSDGsStore();

const userLabels = computed(() => useLabelDecisionsStore.userLabels);
const isLoading = computed(() => useLabelDecisionsStore.isLoading);
const error = computed(() => useLabelDecisionsStore.error);

// Track expanded labels
const expandedLabels = ref<number[]>([]);

// Fetch user labels for a publication on component mount
const publicationId = 88466//30310// 88466;
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
</script>
