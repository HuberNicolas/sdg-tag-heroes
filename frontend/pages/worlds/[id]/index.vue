<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold text-center mb-6">
      {{ sdg?.title || "SDG Leaderboard" }}
    </h1>

    <!-- Loading & Error Handling -->
    <div v-if="loading" class="text-blue-500 text-lg text-center">Loading leaderboard...</div>
    <div v-if="error" class="text-red-500 text-lg text-center">Error: {{ error }}</div>

    <!-- Leaderboard Table -->
    <div v-else-if="leaderboard.length > 0" class="overflow-x-auto">
      <table class="w-full border-collapse border border-gray-300">
        <thead>
        <tr class="bg-gray-200">
          <th class="p-3 border">Rank</th>
          <th class="p-3 border">User</th>
          <th class="p-3 border">Tier</th>
          <th class="p-3 border">XP</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(user, index) in leaderboard" :key="user.user_id" class="text-center">
          <td class="p-3 border">{{ index + 1 }}</td>
          <td class="p-3 border flex items-center gap-2 justify-center">
            <img :src="generateAvatar(user.user.email)" alt="Avatar" class="w-8 h-8 rounded-full" />
            {{ user.user.email }}
          </td>
          <td class="p-3 border">{{ user.rank.tier }}</td>
          <td class="p-3 border">{{ user.rank.xpRequired }}</td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- No Data -->
    <p v-else class="text-gray-600 text-center text-lg">No rankings available for this SDG.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { useSDGsStore } from "~/stores/sdgs";
import { generateAvatar } from "~/utils/avatar";

const route = useRoute();
const sdgRanksStore = useSDGRanksStore();
const sdgsStore = useSDGsStore();

const loading = ref(true);
const error = ref<string | null>(null);
const leaderboard = ref<any[]>([]);

// Get SDG details
const sdgId = computed(() => Number(route.params.id));
const sdg = computed(() => sdgsStore.sdgs.find((s) => s.id === sdgId.value));

onMounted(async () => {
  try {
    await sdgRanksStore.fetchSDGLeaderboard(sdgId.value);
    leaderboard.value = sdgRanksStore.leaderboard;
  } catch (err) {
    console.error("Error fetching leaderboard:", err);
    error.value = err.message || "Failed to load leaderboard.";
  } finally {
    loading.value = false;
  }
});
</script>
