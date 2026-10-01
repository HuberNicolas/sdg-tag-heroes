<template>
  <div class="mt-2">
    <!-- Form Section -->
    <form class="space-y-4" @submit.prevent="submitUserLabel">
      <!-- Comment Input -->
      <div class="flex flex-col">
        <label for="comment" class="text-sm font-medium text-fg">Explain Your Label Choice <span class="font-mono text-xs text-fg-faint">(optional)</span></label>
        <textarea
          id="comment"
          v-model="comment"
          rows="1"
          class="mt-1.5 px-3 py-2 border border-line rounded-[10px] bg-surface-2 text-sm transition focus:outline-none focus:border-accent/60 focus:ring-4 focus:ring-accent/15"
          placeholder="Provide context for your label decision (optional)"
        />
      </div>


      <div class="flex flex-wrap items-center justify-between gap-3 mt-3">
        <div class="flex items-center">
          <!-- Checkbox for Abstract Section -->
          <input
            id="include_abstract_section"
            v-model="includeAbstractSection"
            type="checkbox"
            class="checkbox checkbox-sm checkbox-primary mr-2"

          >
          <label for="include_abstract_section" class="text-sm text-fg-dim">Include Abstract Section</label>
        </div>

        <!-- Submit Button -->
        <div class="flex items-center gap-2">
          <span v-if="!hasPick" class="font-mono text-[11px] text-fg-faint">pick an SDG in the honeycomb first</span>
          <UButton
            icon="i-heroicons-tag"
            size="sm"
            color="primary"
            variant="solid"
            :label="isSubmitting ? 'Submitting…' : 'Submit SDG Label'"
            :loading="isSubmitting"
            :disabled="isSubmitting || !hasPick"
            :trailing="false"
            type="submit"
          />
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
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
const includeAbstractSection = ref(false); // Send the marked abstract passage with the label
const hasPick = computed(() => sdgsStore.getSelectedSDGLabel !== 0);
const toast = useToast();

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
      abstract_section: includeAbstractSection.value ? explanationStore.markedText : null,
      comment: comment.value, // Include the comment if provided
      decision_id: labelDecisionsStore.selectedSDGLabelDecision?.decisionId || null,
      publication_id: labelDecisionsStore.selectedSDGLabelDecision?.publicationId || null,
      decision_type: "CONSENSUS_MAJORITY", // Default decision type
    };

    // Send data to the function
    await createOrLinkSDGUserLabel(userLabelRequest);

    // Show the new vote in the community views (honeycomb, ring, bars)
    if (userLabelRequest.publication_id) {
      await labelDecisionsStore.fetchUserLabelsByPublicationId(userLabelRequest.publication_id);
    }
    toast.add({
      title: "Label submitted",
      description: selectedSDGLabel === -1 ? "You marked the publication as not relevant." : `You labeled the publication with SDG ${selectedSDGLabel}.`,
      icon: "i-heroicons-check-circle",
      color: "primary",
    });

    // Reset fields after submission
    includeAbstractSection.value = false;
    comment.value = "";
    sdgsStore.setSelectedSDGLabel(0);
  } catch (error) {
    console.error("Error submitting SDG label:", error);
    toast.add({
      title: "Label not submitted",
      description: "Something went wrong. Please try again.",
      icon: "i-heroicons-exclamation-triangle",
      color: "red",
    });
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Add custom styles for form or button elements if needed */
</style>
