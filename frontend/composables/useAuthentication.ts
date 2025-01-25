import { useRuntimeConfig, useCookie } from '#app';
import type { LoginSchemaFull, UserDataSchemaFull } from '~/types/authentication';

export default function useAuth() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token'); // Use Nuxt's useCookie

  // Login method
  async function login(credentials: { email: string; password: string }): Promise<LoginSchemaFull> {
    try {
      const response = await $fetch<LoginSchemaFull>(`${config.public.apiUrl}/auth/login`, {
        method: 'POST',
        body: credentials,
      });

      // Store token in a cookie
      accessToken.value = response.access_token; // Set the cookie value
      return response;
    } catch (error) {
      throw new Error(`Login failed: ${error}`);
    }
  }

  // Fetch user profile
  async function getProfile(): Promise<UserDataSchemaFull> {
    try {
      const token = accessToken.value; // Get the token from the cookie
      if (!token) throw new Error('No token available');

      const profile = await $fetch<UserDataSchemaFull>(`${config.public.apiUrl}/auth/protected`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return profile;
    } catch (error) {
      throw new Error(`Failed to fetch profile: ${error}`);
    }
  }

  // Logout method
  function logout(): void {
    accessToken.value = null; // Clear the cookie value
  }

  return {
    login,
    getProfile,
    logout,
  };
}
