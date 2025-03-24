import { defineStore } from "pinia";
import type {
  SDGPrediction, UserCoordinates,
  UserEnrichedInterestsDescription,
  UserEnrichedSkillsDescription
} from "~/types/gptAssistantService";
import type { Stage, Quadrant  } from "~/types/enums";

import {useDimensionalityReductionsStore} from "~/stores/dimensionalityReductions";
import {usePublicationsStore } from "~/stores/publications";
import {useSDGPredictionsStore} from "~/stores/sdgPredictions";
import {useLabelDecisionsStore} from "~/stores/sdgLabelDecisions";

export const useGameStore = defineStore("game", {
  state: () => ({
    level: null as number,
    sdg: null as number,
    showLeaderboard: false,
    quadrant: null as Quadrant | null,
    stage: null as Stage | null,
    selectedScenario: null as string | null, // Multiple scenarios new Set<string>(),

    skillsDescription: {} as UserEnrichedSkillsDescription | null,
    interestsDescription: {} as UserEnrichedInterestsDescription | null,

    proposedSdgFromSkills: {} as SDGPrediction | null,
    proposedSdgFromInterests: {} as SDGPrediction | null,

    userCoordinates: null as UserCoordinates | null
  }),
  actions: {
    setLevel(level: number) {
      this.level = level;
    },

    setSDG(sdg: number) {
      console.log("setSDG", sdg);
      this.sdg = sdg;
    },

    setShowLeaderboard(showLeaderboard: boolean) {
      this.showLeaderboard = showLeaderboard;
    },

    setQuadrant(quadrant: Quadrant) {
      this.quadrant = quadrant;
    },

    setStage(stage: Stage) {
      this.stage = stage;
    },

    toggleScenario(scenario: string) {
      if (this.selectedScenario === scenario) {
        this.selectedScenario = null;
      } else {
        this.selectedScenario = scenario;
      }
      const publicationsStore = usePublicationsStore();
      const sdgPredictionsStore = useSDGPredictionsStore();
      sdgPredictionsStore.selectedPartitionedSDGPredictions = [];
      publicationsStore.selectedPartitionedPublications = [];
    },
    removeScenario(scenario: string) {
      if (this.selectedScenario === scenario) {
        this.selectedScenario = null;
        this.clearScenarioData();
      }
    },
    clearScenarioData() {
      const dimensionalityStore = useDimensionalityReductionsStore();
      const publicationsStore = usePublicationsStore();
      const sdgPredictionsStore = useSDGPredictionsStore();
      const labelDecisionsStore = useLabelDecisionsStore();

      dimensionalityStore.scenarioTypeReductions = [];
      publicationsStore.scenarioTypePublications = [];
      sdgPredictionsStore.scenarioTypeSDGPredictions = [];
      labelDecisionsStore.scenarioTypeSDGLabelDecisions = [];


      // reset Table
      sdgPredictionsStore.selectedPartitionedSDGPredictions = [];
      publicationsStore.selectedPartitionedPublications = [];
    },

    /* Multiple Scenarios
    toggleScenario(scenario: string) {
      if (this.selectedScenarios.has(scenario)) {
        this.selectedScenarios.delete(scenario);
      } else {
        this.selectedScenarios.add(scenario);
      }
    },
    removeScenario(scenario: string) {
      this.selectedScenarios.delete(scenario);
    }, */

    setSkillsDescription(description: UserEnrichedSkillsDescription) {
      this.skillsDescription = description;
    },

    setInterestsDescription(description: UserEnrichedInterestsDescription) {
      this.interestsDescription = description;
    },

    setProposedSdgFromSkills(proposal: SDGPrediction) {
      this.proposedSdgFromSkills = proposal;
    },

    setProposedSdgFromInterests(proposal: SDGPrediction) {
      this.proposedSdgFromInterests = proposal;
    },

    setUserCoordinates(coordinates: UserCoordinates) {
      this.userCoordinates = coordinates;
    },


  },
  getters: {
    getLevel: (state) => state.level,
    getSDG: (state) => state.sdg,
    getQuadrant: (state) => state.quadrant,
    getStage: (state) => state.stage,
    getSkillsDescription: (state) => state.skillsDescription,
    getInterestsDescription: (state) => state.interestsDescription,
    getProposedSdgFromSkills: (state) => state.proposedSdgFromSkills,
    getProposedSdgFromInterests: (state) => state.proposedSdgFromInterests,
    getUserCoordinates: (state) => state.userCoordinates,
    isSelected: (state) => (scenario: string) => state.selectedScenario === scenario,
    selectedScenarioList: (state) => (state.selectedScenario ? [state.selectedScenario] : []),
    /* Multiple Scenarios
    isSelected: (state) => (scenario: string) => state.selectedScenarios.has(scenario),
    selectedScenarioList: (state) => Array.from(state.selectedScenarios),
     */
  },
});
