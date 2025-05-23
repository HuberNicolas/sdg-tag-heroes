<template>
  <div class="container mx-auto p-4">
    <!-- Form Section -->
    <form @submit.prevent="submitUserLabel" class="space-y-4">
      <!-- Comment Input -->
      <div class="flex flex-col">
        <label for="comment" class="text-lg font-medium text-gray-700">Explain Your Label Choice (Optional): Share Your Reasoning with the Community</label>
        <textarea
          id="comment"
          v-model="comment"
          rows="1"
          class="mt-1 p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-500"
          placeholder="Provide context for your label decision (optional)"
        ></textarea>
      </div>


      <div class="flex items-center justify-between mt-4">
        <div>
          <!-- Checkbox for Abstract Section -->
          <input
            type="checkbox"
            v-model="includeAbstractSection"
            class="form-checkbox h-5 w-5 text-gray-600 mr-2"
            id="include_abstract_section"

          />
          <label for="include_abstract_section" class="text-lg font-medium text-gray-700">Include Abstract Section</label>
        </div>

        <!-- Submit Button -->
        <UButton
          icon="heroicons-outline:tag"
          size="sm"
          color="primary"
          variant="solid"
          :label="isSubmitting ? 'Submitting...' : 'Submit SDG Label'"
          :disabled="isSubmitting"
          :trailing="false"
          type="submit"
        />
      </div>
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

  if (selectedSDGLabel === 0) {
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

    // Send data to the function
    await createOrLinkSDGUserLabel(userLabelRequest);

    // Reset fields after submission
    includeAbstractSection.value = false;
    comment.value = "";
    sdgsStore.setSelectedSDGLabel(0);
  } catch (error) {
    console.error("Error submitting SDG label:", error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Add custom styles for form or button elements if needed */
</style>
