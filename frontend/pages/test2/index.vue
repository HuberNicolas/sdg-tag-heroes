<script setup lang="ts">
import { useDimensionalityReductionsStore } from "~/stores/dimensionalityReductions";
import { usePublicationsStore } from "~/stores/publications";
import { useCollectionsStore } from "~/stores/collections";
import { useSDGsStore } from "~/stores/sdgs";
import { useUsersStore } from "~/stores/users"
import { onMounted } from "vue";

const dimensionalityReductionsStore = useDimensionalityReductionsStore();
const publicationsStore = usePublicationsStore();
const collectionsStore = useCollectionsStore();
const sdgsStore = useSDGsStore();
const usersStore = useUsersStore();


// Fetch partitioned dimensionality reductions and publications on component mount
onMounted(async () => {
  const reductionShorthand = "TM-WWF-UMAP-10-0.0-2";
  const partNumber = 9;
  const totalParts = 9;

  await dimensionalityReductionsStore.fetchDimensionalityReductionsPartitioned(reductionShorthand, partNumber, totalParts);
  await publicationsStore.fetchPublicationsForDimensionalityReductionsPartitioned(reductionShorthand, partNumber, totalParts);
  await collectionsStore.fetchCollections()
  await sdgsStore.fetchSDGs();
  await usersStore.fetchUsers();
});

// Access state
const partitionedReductions = computed(() => dimensionalityReductionsStore.partitionedReductions);
const partitionedPublications = computed(() => publicationsStore.partitionedPublications);

const collections = computed(() => collectionsStore.collections);
const sdgs = computed(() => sdgsStore.sdgs);
const users = computed(() => usersStore.users);

const isLoading = computed(() => dimensionalityReductionsStore.isLoading);
const error = computed(() => dimensionalityReductionsStore.error);
</script>

<template>
  <div>
    <h1>Collections</h1>
    <p v-if="isLoading">Loading...</p>
    <p v-else-if="error">{{ error }}</p>
    <ul v-else>
      <li v-for="collection in collections" :key="collection.collectionId">
        <h2>{{ collection.name }}</h2>
        <p>{{ collection.shortName }}</p>
        <p>Count: {{ collection.count }}</p>
      </li>
    </ul>

    <h1>SDGs</h1>
    <p v-if="isLoading">Loading...</p>
    <p v-else-if="error">{{ error }}</p>
    <ul v-else>
      <li v-for="sdg in sdgs" :key="sdg.id">
        <h2>{{ sdg.name }}</h2>
        <p>Color: {{ sdg.color }}</p>
      </li>
    </ul>

    <h1>Users</h1>
    <p v-if="isLoading">Loading...</p>
    <p v-else-if="error">{{ error }}</p>
    <ul v-else>
      <li v-for="user in users" :key="user.userId">
        <h2>{{ user.email }}</h2>
        <p>Roles: {{ user.roles.join(", ") }}</p>
      </li>
    </ul>

    <h1>Partitioned Dimensionality Reductions</h1>
    <p v-if="isLoading">Loading...</p>
    <p v-else-if="error">{{ error }}</p>
    <div v-else>
      <h2>Dimensionality Reductions</h2>
      <ul>
        <li v-for="reduction in partitionedReductions" :key="reduction.dimRedId">
          SDG: {{ reduction.sdg }}, Level: {{ reduction.level }}, Coordinates: ({{ reduction.xCoord }}, {{ reduction.yCoord }})
        </li>
      </ul>

      <h2>Corresponding Publications</h2>
      <ul>
        <li v-for="publication in partitionedPublications" :key="publication.publicationId">
          {{ publication.title }}
        </li>
      </ul>
    </div>
  </div>
</template>
