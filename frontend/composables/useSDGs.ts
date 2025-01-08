import { useRuntimeConfig } from "nuxt/app";
import type { SDGGoal } from "@/types/schemas";


export default class UseSDGGoals {
  private config = useRuntimeConfig();

  // Fetch SDG goals without targets
  async getSDGGoals(): Promise<SDGGoal[]> {
    try {
      // Retrieve the access token from localStorage
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("No access token found");
      }

      // Construct the API URL
      const url = `${this.config.public.apiUrl}sdgs?include_targets=false`;

      // Make the API request using $fetch
      const data = await $fetch<SDGGoal[]>(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // Return the data
      return data;
    } catch (error) {
      console.error("Failed to fetch SDG goals", error);
      throw new Error("Failed to fetch SDG goals");
    }
  }
}
