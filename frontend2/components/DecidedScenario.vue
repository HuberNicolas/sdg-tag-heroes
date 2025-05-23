<template>
  <div v-if="selectedSDGLabelDecision && selectedSDGLabelDecision.scenarioType === 'Decided'">
    <NuxtLink :to="`/publications/labels/${selectedSDGLabelDecision.publicationId}`">
      Details
    </NuxtLink>

    <!-- Display User Avatars for Annotators -->
    <div v-if="annotators.length > 0" class="flex flex-wrap gap-2 mt-4">
      <h3 class="w-full text-sm font-semibold text-gray-700">Annotators</h3>
      <div v-for="user in annotators" :key="user.userId" class="flex items-center">
        <img
          :src="generateAvatar(user.email)"
          :alt="`Avatar of ${user.email}`"
          class="w-3 h-3 rounded-full"
        />
      </div>
    </div>

    <!-- Display User Avatars for Labelers -->
    <div v-if="labelers.length > 0" class="flex flex-wrap gap-2 mt-4">
      <h3 class="w-full text-sm font-semibold text-gray-700">Labelers</h3>
      <div v-for="user in labelers" :key="user.userId" class="flex items-center">
        <img
          :src="generateAvatar(user.email)"
          :alt="`Avatar of ${user.email}`"
          class="w-3 h-3 rounded-full"
        />
      </div>
    </div>

    <!-- QuestButton for Decided Scenario -->
    <QuestButton
      icon="line-md-confirm-square"
      name="Decided"
      tooltip="Decided"
    />

    <!-- Display SDG Icon -->
    <div v-if="currentSDG" class="mt-4">
      <img
        :src="`data:image/svg+xml;base64,${currentSDG.icon}`"
        :alt="`SDG ${currentSDG.id} Icon`"
        class="w-4 h-4 mb-4"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useSDGsStore } from "~/stores/sdgs";
import { useUsersStore } from "~/stores/users";
import { generateAvatar } from "~/utils/avatar";

// Use stores
const labelDecisionsStore = useLabelDecisionsStore();
const sdgsStore = useSDGsStore();
const usersStore = useUsersStore();

// Computed properties
const selectedSDGLabelDecision = computed(() => labelDecisionsStore.selectedSDGLabelDecision);
const currentSDG = computed(() => {
  if (selectedSDGLabelDecision.value) {
    return sdgsStore.sdgs.find(sdg => sdg.id === selectedSDGLabelDecision.value.decidedLabel) || null;
  }
  return null;
});

// Annotators: Users who contributed annotations
const annotators = computed(() => {
  if (selectedSDGLabelDecision.value) {
    return selectedSDGLabelDecision.value.annotations
      .map(annotation => usersStore.users.find(user => user.userId === annotation.userId))
      .filter(user => user !== undefined);
  }
  return [];
});

// Labelers: Users who contributed labels
// Currently, all are shown, maybe distinguish who contributed to true label
const labelers = computed(() => {
  if (selectedSDGLabelDecision.value && labelDecisionsStore.userLabels) {
    return labelDecisionsStore.userLabels
      .filter(label => label.publicationId === selectedSDGLabelDecision.value.publicationId)
      .map(label => usersStore.users.find(user => user.userId === label.userId))
      .filter(user => user !== undefined);
  }
  return [];
});
</script>
