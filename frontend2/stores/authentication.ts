import { defineStore } from 'pinia';
import type { UserDataSchemaFull } from '~/types/authentication';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    userProfile: null as UserDataSchemaFull | null,
  }),
  actions: {
    setUserProfile(profile: UserDataSchemaFull) {
      this.userProfile = profile;
      this.isAuthenticated = true;
    },
    clearUserProfile() {
      this.userProfile = null;
      this.isAuthenticated = false;
    },
  },
});
