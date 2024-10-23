import { useRuntimeConfig } from 'nuxt/app';
import type { PublicationSchema } from '@/types/schemas'; // Assuming you save interfaces in a types folder

export default class PublicationService {
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

      const response = await $fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response;
    } catch (error) {
      throw new Error('Failed to fetch publications');
    }
  }
}
