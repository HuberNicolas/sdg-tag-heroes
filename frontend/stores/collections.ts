import { defineStore } from "pinia";
import type {
  CollectionSchemaBase,
  CollectionSchemaFull,
} from "~/types/collections";
import useCollections from "~/composables/useCollections";

export const useCollectionsStore = defineStore("collections", {
  state: () => ({
    collections: [] as CollectionSchemaFull[],
    collectionDetails: null as CollectionSchemaFull | null,
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    // Fetch all collections
    async fetchCollections() {
      this.isLoading = true;
      this.error = null;

      try {
        const { getCollections } = useCollections();
        this.collections = await getCollections();
      } catch (error) {
        this.error = `Failed to fetch collections: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch a single collection by ID
    async fetchCollectionById(collectionId: number) {
      this.isLoading = true;
      this.error = null;

      try {
        const { getCollectionById } = useCollections();
        this.collectionDetails = await getCollectionById(collectionId);
      } catch (error) {
        this.error = `Failed to fetch collection: ${error}`;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
