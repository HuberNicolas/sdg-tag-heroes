import { defineStore } from 'pinia';
import useXPBanks from '~/composables/useXPBanks';
import type { SDGXPBankSchemaFull, SDGXPBankHistorySchemaFull } from '~/types/sdgXpBank';
import useXPBankHistories from "~/composables/useXPBankHistories";

export const useXPBanksStore = defineStore('xpBanks', {
  state: () => ({
    xpBanks: [] as SDGXPBankSchemaFull[],
    userXPBank: null as SDGXPBankSchemaFull | null,
    xpBankHistory: [] as SDGXPBankHistorySchemaFull[],
    latestXPBankHistory: null as SDGXPBankHistorySchemaFull | null,
  }),

  actions: {
    // Fetch all XP banks
    async fetchXPBanks() {
      const { getXPBanks } = useXPBanks();
      this.xpBanks = await getXPBanks();
    },

    // Fetch a single XP bank by user ID
    async fetchXPBankByUserId(userId: number) {
      const { getXPBankByUserId } = useXPBanks();
      this.userXPBank = await getXPBankByUserId(userId);
    },

    // Fetch the personal XP bank for the current user
    async fetchPersonalXPBank() {
      const { getPersonalXPBank } = useXPBanks();
      this.userXPBank = await getPersonalXPBank();
    },

    // Fetch the latest XP bank history
    async fetchLatestXPBankHistory() {
      const { getLatestXPBankHistory } = useXPBankHistories();
      this.latestXPBankHistory = await getLatestXPBankHistory();
    },

    // Fetch XP bank history for a specific user
    async fetchXPBankHistory(userId: number) {
      const { getXPBankHistory } = useXPBanks();
      this.xpBankHistory = await getXPBankHistory(userId);
    },

    // Add an XP bank increment for a specific user
    async addXPBankIncrement(userId: number, incrementData: { sdg: string; increment: number; reason?: string }) {
      const { addXPBankIncrement } = useXPBanks();
      const newHistory = await addXPBankIncrement(userId, incrementData);
      this.xpBankHistory.unshift(newHistory); // Add the new history entry to the top of the list
      if (this.userXPBank) {
        this.currentXPBank.totalXp += incrementData.increment; // Update the total XP
      }
    },
  },

  getters: {
    // Get all XP banks
    getAllXPBanks: (state) => state.xpBanks,

    // Get the current XP bank
    getUserXPBank: (state) => state.userXPBank,

    // Get XP bank history
    getXPBankHistory: (state) => state.xpBankHistory,
  },
});
