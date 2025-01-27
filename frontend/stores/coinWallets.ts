import { defineStore } from 'pinia';
import useCoinWallets from '~/composables/useCoinWallets';
import type { SDGCoinWalletSchemaFull, SDGCoinWalletHistorySchemaFull } from '~/types/sdgCoinWallet';

export const useCoinWalletsStore = defineStore('coinWallets', {
  state: () => ({
    sdgCoinWallets: [] as SDGCoinWalletSchemaFull[],
    currentSDGCoinWallet: null as SDGCoinWalletSchemaFull | null,
  }),

  actions: {
    // Fetch all SDG coin wallets
    async fetchSDGCoinWallets() {
      const { getSDGCoinWallets } = useCoinWallets();
      this.sdgCoinWallets = await getSDGCoinWallets();
    },

    // Fetch a single SDG coin wallet by user ID
    async fetchSDGCoinWalletByUserId(userId: number) {
      const { getSDGCoinWalletByUserId } = useCoinWallets();
      this.currentSDGCoinWallet = await getSDGCoinWalletByUserId(userId);
    },

    // Fetch the personal SDG coin wallet for the current user
    async fetchPersonalSDGCoinWallet() {
      const { getPersonalSDGCoinWallet } = useCoinWallets();
      this.currentSDGCoinWallet = await getPersonalSDGCoinWallet();
    },

    // Fetch SDG coin wallet history for a specific user
    async fetchSDGCoinWalletHistory(userId: number) {
      const { getSDGCoinWalletHistory } = useCoinWallets();
      this.sdgCoinWalletHistory = await getSDGCoinWalletHistory(userId);
    },

    // Add a wallet increment for a specific user
    async addSDGCoinWalletIncrement(userId: number, incrementData: { increment: number; reason?: string }) {
      const { addSDGCoinWalletIncrement } = useCoinWallets();
      const newHistory = await addSDGCoinWalletIncrement(userId, incrementData);
      this.sdgCoinWalletHistory.unshift(newHistory); // Add the new history entry to the top of the list
      if (this.currentSDGCoinWallet) {
        this.currentSDGCoinWallet.totalCoins += incrementData.increment; // Update the total coins
      }
    },
  },

  getters: {
    // Get all SDG coin wallets
    getAllSDGCoinWallets: (state) => state.sdgCoinWallets,

    // Get the current SDG coin wallet
    getCurrentSDGCoinWallet: (state) => state.currentSDGCoinWallet,

    // Get SDG coin wallet history
    getSDGCoinWalletHistory: (state) => state.sdgCoinWalletHistory,
  },
});
