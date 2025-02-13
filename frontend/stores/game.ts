import { defineStore } from "pinia";
import type {
  SDGPrediction, UserCoordinates,
  UserEnrichedInterestsDescription,
  UserEnrichedSkillsDescription
} from "~/types/gptAssistantService";
import type { Stage, Quadrant  } from "~/types/enums";


export const useGameStore = defineStore("game", {
  state: () => ({
    level: null as number,
    sdg: null as number,
    showLeaderboard: false,
    quadrant: null as Quadrant | null,
    stage: null as Stage | null,

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
    getUserCoordinates: (state) => state.userCoordinates
  },
});
