import { useRuntimeConfig } from "nuxt/app";
import type { PublicationSchema } from "@/types/schemas";

export default class UsePublication {
  private config = useRuntimeConfig();

  // Fetch publications with optional includes and pagination
  async getPublications(include: string[] = [], page: number = 1): Promise<{ items: PublicationSchema[]; page: number; pages: number }> {

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token found');
      }

      const includeParam = include.length > 0 ? `include=${encodeURIComponent(include.join(','))}` : '';
      const url = `${this.config.public.apiUrl}publications?${includeParam}&page=${page}`;

      return await $fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error(`Failed to fetch publications`, error);
      throw new Error('Failed to fetch publications');
    }
  }


  async getPublicationById(include: string[] = [], id: number): Promise<PublicationSchema> {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token found');
      }

      // Encode the include parameter if provided
      const includeParam = include.length > 0 ? `include=${encodeURIComponent(include.join(','))}` : '';
      const url = `${this.config.public.apiUrl}publications/${id}?${includeParam}`;

      // Fetch the publication from the API
      return await $fetch<PublicationSchema>(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error(`Failed to fetch publication with ID ${id}:`, error);
      throw new Error('Failed to fetch publication');
    }
  }
}
