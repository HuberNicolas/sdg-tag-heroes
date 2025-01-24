import { defineStore } from "pinia";
import type {
  UserSchemaFull,
} from "~/types/users";
import useUsers from "~/composables/useUsers";

export const useUsersStore = defineStore("users", {
  state: () => ({
    users: [] as UserSchemaFull[],
    userDetails: null as UserSchemaFull | null,
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    // Fetch all users
    async fetchUsers(role?: string) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getUsers } = useUsers();
        this.users = await getUsers(role);
      } catch (error) {
        this.error = `Failed to fetch users: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a single user by ID
    async fetchUserById(userId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getUserById } = useUsers();
        this.userDetails = await getUserById(userId);
      } catch (error) {
        this.error = `Failed to fetch user: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch users by IDs
    async fetchUsersByIds(userIds: number[]) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getUsersByIds } = useUsers();
        this.users = await getUsersByIds(userIds);
      } catch (error) {
        this.error = `Failed to fetch users by IDs: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
