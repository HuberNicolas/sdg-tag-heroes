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

  async getPublicationsBySDGValues(
    sdgRange = [0.98, 0.99], // Default SDG range
    limit = 10, // Default limit per SDG
    sdgs = [], // List of SDGs to filter
    include = [], // Related entities to include
    model = null, // Specific model name to filter by
  ) {
    try {
      // Retrieve the access token from localStorage
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token found');
      }

      // Construct query parameters
      const params = new URLSearchParams();
      params.append('limit', limit.toString());

      if (sdgRange.length > 0) {
        sdgRange.forEach((range) => params.append('sdg_range', range.toString()));
      }

      // Append the SDGs if provided
      if (sdgs.length > 0) {
        sdgs.forEach((sdg) => params.append('sdgs', sdg.toString()));
      }

      // Include related entities if specified
      if (include.length > 0) {
        params.append('include', include.join(','));
      }
      params.append('include', 'dim_red');

      // Append the model if specified
      if (model) {
        params.append('model', model);
      }

      // Construct the full API URL
      const url = `${this.config.public.apiUrl}publications/by-sdg-values?${params.toString()}`;

      // Make the API request using `$fetch`
      // Return the response data
      return await $fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error(`Failed to fetch publications by SDG values`, error);
      throw new Error('Failed to fetch publications by SDG values');
    }
  }
}
