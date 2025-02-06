import { defineStore } from "pinia";
import type {
  SDGPrediction, UserCoordinates,
  UserEnrichedInterestsDescription,
  UserEnrichedSkillsDescription
} from "~/types/gptAssistantService";


export const useGameStore = defineStore("game", {
  state: () => ({
    level: null as number,
    sdg: null as number,

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
      this.sdg = sdg;
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
    getSkillsDescription: (state) => state.skillsDescription,
    getInterestsDescription: (state) => state.interestsDescription,
    getProposedSdgFromSkills: (state) => state.proposedSdgFromSkills,
    getProposedSdgFromInterests: (state) => state.proposedSdgFromInterests,
    getUserCoordinates: (state) => state.userCoordinates
  },
});
