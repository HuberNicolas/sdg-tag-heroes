import { defineStore } from "pinia";

import type { AnnotationSchemaBase, AnnotationSchemaFull } from "~/types/annotation";
import type { SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull } from "~/types/sdgLabelDecision";
import type { SDGUserLabelSchemaBase, SDGUserLabelSchemaFull, SDGUserLabelsCommentSummarySchema } from "~/types/sdgUserLabel";
import type { VoteSchemaBase, VoteSchemaFull } from "~/types/vote";

import useAnnotations from "~/composables/useAnnotations";
import useSDGLabelDecisions from "~/composables/useSDGLabelDecisions";
import useUserLabels from "~/composables/useUserLabels";
import useVotes from "~/composables/useVotes";

export const useLabelDecisionsStore = defineStore("labelDecisions", {
  state: () => ({
    sdgLabelDecisions: null as SDGLabelDecisionSchemaFull[] | null,

    partitionedSDGLabelDecisions: [] as SDGLabelDecisionSchemaFull[], // All SDGs
    sdgLevelSDGLabelDecisions: [] as SDGLabelDecisionSchemaFull[], // 1 SDG

    showAllSDGUserLabels: false, // Default: show only the latest SDG User Labels

    scenarioTypeSDGLabelDecisions: [] as SDGLabelDecisionSchemaFull[],

    totalVotes: 0 as number,
    voteDistribution: {},


    selectedSDGLabelDecision: null as SDGLabelDecisionSchemaFull | null,
    userLabels: [] as SDGUserLabelSchemaFull[],
    annotations: [] as AnnotationSchemaFull[],
    votes: [] as VoteSchemaFull[],
    commentSummary: null as SDGUserLabelsCommentSummarySchema | null,

    isLoading: false,
    error: null as string | null,
  }),
  actions: {

    updateVoteStatistics() {
      const voteCounts = {};
      this.userLabels.forEach(label => {
        const votedLabel = label.votedLabel;
        if ((votedLabel >= 1 && votedLabel <= 17) || votedLabel === -1) {
          voteCounts[votedLabel] = (voteCounts[votedLabel] || 0) + 1;
        }
      });

      this.voteDistribution = voteCounts;
      this.totalVotes = Object.values(voteCounts).reduce((sum, count) => sum + count, 0);
    },


    // Fetch SDG Label Decision by Publication ID
    async fetchSDGLabelDecisionsByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGLabelDecisionsByPublicationId } = useSDGLabelDecisions();
        const decisions = await getSDGLabelDecisionsByPublicationId(publicationId);
        this.sdgLabelDecisions = decisions || null;
      } catch (error) {
        this.error = `Failed to fetch SDG label decision: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // TODO: fix, as we currently return all
    // Fetch single SDG Label Decision by Publication ID
    async fetchSDGLabelDecisionByPublicationId(publicationId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGLabelDecisionsByPublicationId } = useSDGLabelDecisions();
        const decisions = await getSDGLabelDecisionsByPublicationId(publicationId);
        this.selectedSDGLabelDecision = decisions[0] || null;
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
        this.updateVoteStatistics();
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

    // Fetch Comment Summary by User Label IDs
    async fetchCommentSummary(userLabelIds: number[]) {
      this.isLoading = true;
      this.error = null;

      try {
        const { createCommentSummary } = useSDGLabelDecisions();
        const summary = await createCommentSummary(userLabelIds);
        this.commentSummary = summary || null;
      } catch (error) {
        this.error = `Failed to fetch comment summary: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch Newest SDG Label Decisions for Reduction
    async fetchSDGLabelDecisionsForReduction(sdg: number, reductionShorthand: string, level: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getSDGLabelDecisionsForReduction } = useSDGLabelDecisions();
        const decisions = await getSDGLabelDecisionsForReduction(sdg, reductionShorthand, level);
        this.sdgLevelSDGLabelDecisions = decisions || [];

      } catch (error) {
        this.error = `Failed to fetch newest SDG Label Decisions: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchAnnotationsByDecisionId(decisionId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getAnnotationsByDecisionId } = useAnnotations();
        this.annotations = await getAnnotationsByDecisionId(decisionId);
      } catch (error) {
        this.error = `Failed to fetch annotations for decision ID ${decisionId}: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchScenarioSDGLabelDecisionsForReduction(sdg: number, reductionShorthand: string, scenarioType: string) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getScenarioSDGLabelDecisionsForReduction } = useSDGLabelDecisions();
        const decisions = await getScenarioSDGLabelDecisionsForReduction(sdg, reductionShorthand, scenarioType);
        this.scenarioTypeSDGLabelDecisions = decisions || [];
      } catch (error) {
        this.error = `Failed to fetch scenario SDG Label Decisions: ${error}`;
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

    toggleShowAllSDGUserLabels() {
      this.showAllSDGUserLabels = !this.showAllSDGUserLabels;
    },

  },
});
