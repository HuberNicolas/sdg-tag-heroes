import { useRuntimeConfig } from "nuxt/app";

export default class UseAuth {

  private config = useRuntimeConfig();


  // Login method using $fetch
  async login(credentials: { email: string, password: string }) {
    try {
      const response = await $fetch(`${this.config.public.backendURL}token/`, {
        method: 'POST',
        body: credentials
      });

      // Store tokens in localStorage
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);

    } catch (error) {
      throw new Error('Login failed: ', error);
    }
  }

  // Fetch the user profile using $fetch
  async getProfile() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No token available');
      }

      // contains user profile data (email, role, etc.)
      return await $fetch(`${this.config.public.apiUrl}auth/protected`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
    } catch (error) {
      throw new Error('Failed to fetch profile: ', error);
    }
  }



  // Logout method
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}
