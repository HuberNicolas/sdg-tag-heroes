import { useRuntimeConfig } from "nuxt/app";
import type {
  CollectionSchemaBase,
  CollectionSchemaFull,
} from "~/types/collections";

export default function useCollections() {
  const config = useRuntimeConfig();

  // Fetch all collections
  async function getCollections(): Promise<CollectionSchemaFull[]> {
    try {
      return await $fetch<CollectionSchemaFull[]>(`${config.public.apiUrl}/collections`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
    } catch (error) {
      throw new Error(`Failed to fetch collections: ${error}`);
    }
  }

  // Fetch a single collection by ID
  async function getCollectionById(collectionId: number): Promise<CollectionSchemaFull> {
    try {
      return await $fetch<CollectionSchemaFull>(
        `${config.public.apiUrl}/collections/${collectionId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );
    } catch (error) {
      throw new Error(`Failed to fetch collection: ${error}`);
    }
  }

  return {
    getCollections,
    getCollectionById,
  };
}
