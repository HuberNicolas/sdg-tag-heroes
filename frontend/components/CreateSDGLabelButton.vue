<template>
  <div class="container mx-auto p-4">
    <button
      @click="submitUserLabel"
      class="px-4 py-2 bg-green-600 text-white rounded-lg shadow hover:bg-green-700 disabled:bg-gray-400"
    >
      {{ isSubmitting ? "Submitting..." : "Submit SDG Label" }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users";
import useUserLabels from "~/composables/useUserLabels";


const sdgsStore = useSDGsStore();
const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();

const isSubmitting = ref(false);

const {createOrLinkSDGUserLabel} = useUserLabels();

const submitUserLabel = async () => {
  const currentUser = usersStore.getCurrentUser;
  const selectedSDGLabel = sdgsStore.getSelectedSDGLabel;

  if (!currentUser) {
    alert("You need to be logged in to submit an SDG label.");
    return;
  }

  if (selectedSDGLabel === 0) {
    alert("Please select an SDG before submitting.");
    return;
  }

  isSubmitting.value = true;

  try {
    const userLabelRequest = {
      user_id: currentUser.userId,
      voted_label: selectedSDGLabel,
      decision_id: labelDecisionsStore.selectedSDGLabelDecision?.decisionId || null,
      publication_id: labelDecisionsStore.selectedSDGLabelDecision?.publicationId || null,
      decision_type: "CONSENSUS_MAJORITY", // Default decision type
    };
    console.log(userLabelRequest);

    // Send data to the function
    await createOrLinkSDGUserLabel(userLabelRequest);
    alert("SDG Label submitted successfully!");

    // Reset selected SDG after submission
    selectedSDGLabel.value = 0;
  } catch (error) {
    alert("Failed to submit SDG label. Please try again.");
    console.error("Error submitting SDG label:", error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

