import { defineStore } from "pinia";


export const useGameStore = defineStore("game", {
  state: () => ({
    level: 1,
  }),
  actions: {
    setLevel(level: number) {
      this.level = level;
    },

  },
  getters: {
    getLevel: (state) => state.level,
  },
});
