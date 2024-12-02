import { useRuntimeConfig } from "nuxt/app";
import type { UserSchema } from "@/types/userSchema";

export default class UseUser {
  private config = useRuntimeConfig();

  /**
   * Fetch users with optional role filter and pagination
   * @param {string | null} role - Role to filter by (optional)
   * @param {number} page - Page number for pagination
   * @returns {Promise<{ items: UserSchema[]; page: number; pages: number }>}
   */
  async getUsers(role: string | null = null, page: number = 1): Promise<{ items: UserSchema[]; page: number; pages: number }> {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("No access token found");
      }

      const roleParam = role ? `role=${encodeURIComponent(role)}` : "";
      const url = `${this.config.public.apiUrl}users?${roleParam}&page=${page}`;

      return await $fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error("Failed to fetch users", error);
      throw new Error("Failed to fetch users");
    }
  }

  /**
   * Fetch a user by their ID
   * @param {number} id - User ID
   * @returns {Promise<UserSchema>}
   */
  async getUserById(id: number): Promise<UserSchema> {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("No access token found");
      }

      const url = `${this.config.public.apiUrl}users/${id}`;

      return await $fetch<UserSchema>(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error(`Failed to fetch user with ID ${id}:`, error);
      throw new Error("Failed to fetch user");
    }
  }
}
