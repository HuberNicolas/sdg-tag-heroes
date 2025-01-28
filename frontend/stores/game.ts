import { defineStore } from "pinia";
import type {
  SDGPrediction,
  UserEnrichedInterestsDescription,
  UserEnrichedSkillsDescription
} from "~/types/gptAssistantService";


export const useGameStore = defineStore("game", {
  state: () => ({
    level: 1,

    skillsDescription: {} as UserEnrichedSkillsDescription | null,
    interestsDescription: {} as UserEnrichedInterestsDescription | null,

    proposedSdgFromSkills: {} as SDGPrediction | null,
    proposedSdgFromInterests: {} as SDGPrediction | null,
  }),
  actions: {
    setLevel(level: number) {
      this.level = level;
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


  },
  getters: {
    getLevel: (state) => state.level,
    getSkillsDescription: (state) => state.skillsDescription,
    getInterestsDescription: (state) => state.interestsDescription,
    getProposedSdgFromSkills: (state) => state.proposedSdgFromSkills,
    getProposedSdgFromInterests: (state) => state.proposedSdgFromInterests,
  },
});
