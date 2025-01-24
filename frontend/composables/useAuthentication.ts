import {useRuntimeConfig} from "nuxt/app";
import type {
  LoginSchemaFull,
  UserDataSchemaFull,
  TokenDataSchemaBase,
} from '~/types/authentication';

export default function useAuthentication() {
  const config = useRuntimeConfig();

  // Reactive state for authentication
  const isAuthenticated = ref(false);
  const userProfile = ref<UserDataSchemaFull | null>(null);

  // Login method using $fetch
  async function login(credentials: { email: string; password: string }): Promise<LoginSchemaFull> {
    try {
      const response = await $fetch<LoginSchemaFull>(`${config.public.apiUrl}/auth/login`, {
        method: 'POST',
        body: credentials,
      });

      // Store tokens in localStorage
      localStorage.setItem('access_token', response.access_token);
      isAuthenticated.value = true;

      return response;
    } catch (error) {
      throw new Error(`Login failed: ${error}`);
    }
  }

  // Fetch the user profile using $fetch
  async function getProfile(): Promise<UserDataSchemaFull> {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No token available');
      }

      const profile = await $fetch<UserDataSchemaFull>(`${config.public.apiUrl}/auth/protected`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // Update reactive state
      userProfile.value = profile;
      return profile;
    } catch (error) {
      throw new Error(`Failed to fetch profile: ${error}`);
    }
  }

  // Logout method
  function logout(): void {
    localStorage.removeItem('access_token');
    isAuthenticated.value = false;
    userProfile.value = null;
  }

  return {
    isAuthenticated,
    userProfile,
    login,
    getProfile,
    logout,
  };
}
