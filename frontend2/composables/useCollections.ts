import { useCookie, useRuntimeConfig } from "nuxt/app";
import { snakeToCamel } from "../utils/snakeToCamel";
import type { CollectionSchemaFull } from "~/types/collections";

export default function useCollections() {
  const config = useRuntimeConfig();
  const accessToken = useCookie('access_token');

  // Fetch all collections
  async function getCollections(): Promise<CollectionSchemaFull[]> {
    try {
      const response=  await $fetch<CollectionSchemaFull[]>(`${config.public.apiUrl}/collections`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch collections: ${error}`);
    }
  }

  // Fetch a single collection by ID
  async function getCollectionById(collectionId: number): Promise<CollectionSchemaFull> {
    try {
      const response = await $fetch<CollectionSchemaFull>(
        `${config.public.apiUrl}/collections/${collectionId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch collection: ${error}`);
    }
  }

  return {
    getCollections,
    getCollectionById,
  };
}
