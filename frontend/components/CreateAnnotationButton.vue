<template>
  <div class="container mx-auto p-4">
    <UButton
      icon="i-heroicons-paper-clip"
      size="sm"
      color="primary"
      variant="solid"
      :label="isSubmitting ? 'Submitting...' : 'Submit Annotation'"
      :disabled="isSubmitting"
      :trailing="false"
      @click="submitAnnotation"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useExplanationsStore } from "~/stores/explanations";
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";
import { useUsersStore } from "~/stores/users"; // Use users store to get current user
import useAnnotations from "~/composables/useAnnotations";

const explanationStore = useExplanationsStore();
const labelDecisionsStore = useLabelDecisionsStore();
const usersStore = useUsersStore();

const isSubmitting = ref(false);

const {createAnnotation} = useAnnotations();

const submitAnnotation = async () => {
  const currentUser = usersStore.getCurrentUser;

  if (!currentUser) {
    alert("You need to be logged in to submit an annotation.");
    return;
  }

  if (!explanationStore.markedText || !explanationStore.comment) {
    alert("Please select a passage and add a comment before submitting.");
    return;
  }

  isSubmitting.value = true;

  try {
    const annotationRequest = {
      user_id: currentUser.userId,
      passage: explanationStore.markedText,
      decision_id: labelDecisionsStore.selectedSDGLabelDecision?.decisionId || null,
      labeler_score: 1, // Example score, update as needed
      comment: explanationStore.comment,
    };

    await createAnnotation(annotationRequest);

    // Optionally, clear inputs after submission
    //explanationStore.setMarkedText("");
    //explanationStore.setComment("");
  } catch (error) {
    alert("Failed to submit annotation. Please try again.");
    console.error("Error submitting annotation:", error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
