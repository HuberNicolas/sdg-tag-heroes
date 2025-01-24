import { useRuntimeConfig } from "nuxt/app";
import type {
  UserSchemaFull,
} from "~/types/users";

export default function useUsers() {
  const config = useRuntimeConfig();

  // Fetch all users
  async function getUsers(role?: string): Promise<UserSchemaFull[]> {
    try {
      return await $fetch<UserSchemaFull[]>(`${config.public.apiUrl}/users`, {
        query: { role },
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
    } catch (error) {
      throw new Error(`Failed to fetch users: ${error}`);
    }
  }

  // Fetch a single user by ID
  async function getUserById(userId: number): Promise<UserSchemaFull> {
    try {
      return await $fetch<UserSchemaFull>(
        `${config.public.apiUrl}/users/${userId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );
    } catch (error) {
      throw new Error(`Failed to fetch user: ${error}`);
    }
  }

  // Fetch users by IDs
  async function getUsersByIds(userIds: number[]): Promise<UserSchemaFull[]> {
    try {
      return await $fetch<UserSchemaFull[]>(`${config.public.apiUrl}/users`, {
        method: "POST",
        body: { user_ids: userIds },
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
    } catch (error) {
      throw new Error(`Failed to fetch users by IDs: ${error}`);
    }
  }

  return {
    getUsers,
    getUserById,
    getUsersByIds,
  };
}
