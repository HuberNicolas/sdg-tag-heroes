<template>
  <div class="container mx-auto p-4">
    <!-- Form Section -->
    <form @submit.prevent="submitUserLabel" class="space-y-4">
      <!-- Checkbox for Abstract Section -->
      <div class="flex items-center">
        <input
          type="checkbox"
          v-model="includeAbstractSection"
          id="include_abstract_section"
          class="mr-2"
        />
        <label for="include_abstract_section" class="text-lg font-medium text-gray-700">Include Abstract Section</label>
      </div>

      <!-- Comment Input -->
      <div class="flex flex-col">
        <label for="comment" class="text-lg font-medium text-gray-700">Comment (Optional)</label>
        <textarea
          id="comment"
          v-model="comment"
          rows="4"
          class="mt-1 p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Add a comment (optional)"
        ></textarea>
      </div>

      <!-- Submit Button -->
      <UButton
        icon="i-heroicons-check-circle"
      size="sm"
      color="primary"
      variant="solid"
      :label="isSubmitting ? 'Submitting...' : 'Submit SDG Label'"
      :disabled="isSubmitting"
      :trailing="false"
      type="submit"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users";
import useUserLabels from "~/composables/useUserLabels";
import { useExplanationsStore } from "~/stores/explanations";

// Store references
const sdgsStore = useSDGsStore();
const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();
const explanationStore = useExplanationsStore();

// Reactive properties
const isSubmitting = ref(false);
const comment = ref(""); // Comment input field

// Function for submitting the SDG label
const { createOrLinkSDGUserLabel } = useUserLabels();

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
      abstract_section: explanationStore.markedText,
      comment: comment.value, // Include the comment if provided
      decision_id: labelDecisionsStore.selectedSDGLabelDecision?.decisionId || null,
      publication_id: labelDecisionsStore.selectedSDGLabelDecision?.publicationId || null,
      decision_type: "CONSENSUS_MAJORITY", // Default decision type
    };


    console.log(userLabelRequest);

    // Send data to the function
    await createOrLinkSDGUserLabel(userLabelRequest);
    alert("SDG Label submitted successfully!");

    // Reset fields after submission
    includeAbstractSection.value = false;
    comment.value = "";
    sdgsStore.setSelectedSDGLabel(0);
  } catch (error) {
    alert("Failed to submit SDG label. Please try again.");
    console.error("Error submitting SDG label:", error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Add custom styles for form or button elements if needed */
</style>
