import { defineStore } from "pinia";

import type { AnnotationSchemaBase, AnnotationSchemaFull } from "~/types/annotation";
import type { SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull } from "~/types/sdgLabelDecision";
import type { SDGUserLabelSchemaBase, SDGUserLabelSchemaFull } from "~/types/sdgUserLabel";
import type { VoteSchemaBase, VoteSchemaFull } from "~/types/vote";

import useAnnotations from "~/composables/useAnnotations";
import useSDGLabelDecisions from "~/composables/useSDGLabelDecisions";
import useUserLabels from "~/composables/useUserLabels";
import useVotes from "~/composables/useVotes";

export const useSDGUserDecisionsStore = defineStore("userDecisions", {
  state: () => ({
    sdgLabelDecision: null as SDGLabelDecisionSchemaFull | null,
    userLabels: [] as SDGUserLabelSchemaFull[],
    annotations: [] as AnnotationSchemaFull[],
    votes: [] as VoteSchemaFull[],

    selectedUserLabel: null as SDGUserLabelSchemaFull | null,
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    // Fetch SDG Label Decision by Publication ID
    async fetchSDGLabelDecisionByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGLabelDecisionsByPublicationId } = useSDGLabelDecisions();
        const decisions = await getSDGLabelDecisionsByPublicationId(publicationId);
        this.sdgLabelDecision = decisions[0] || null; // Assuming only one decision per publication
      } catch (error) {
        this.error = `Failed to fetch SDG label decision: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch User Labels by Publication ID
    async fetchUserLabelsByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGUserLabelsByPublicationId } = useUserLabels();
        this.userLabels = await getSDGUserLabelsByPublicationId(publicationId);
      } catch (error) {
        this.error = `Failed to fetch user labels: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch Annotations for a User Label
    async fetchAnnotationsByUserLabelId(labelId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getAnnotations } = useAnnotations();
        this.annotations = await getAnnotations(); // Filter annotations by labelId if needed
      } catch (error) {
        this.error = `Failed to fetch annotations: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch Votes for an Annotation
    async fetchVotesByAnnotationId(annotationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getVotes } = useVotes();
        this.votes = await getVotes(); // Filter votes by annotationId if needed
      } catch (error) {
        this.error = `Failed to fetch votes: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Select a User Label
    selectUserLabel(label: SDGUserLabelSchemaFull | null) {
      this.selectedUserLabel = label;
    },

    // Clear Selected User Label
    clearSelectedUserLabel() {
      this.selectedUserLabel = null;
    },
  },
});
