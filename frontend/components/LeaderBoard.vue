<template>
  <div class="p-5">
    <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">
      Leaderboard - {{ currentSDG ? `SDG${currentSDG.id} - ${currentSDG.shortTitle}` : "Please select an SDG" }}
    </h1>

    <!-- Loading State -->
    <div v-if="loading" class="text-blue-500 text-lg text-center">Loading leaderboard...</div>

    <!-- Error State -->
    <div v-if="error" class="text-red-500 text-lg text-center">
      <p>An error occurred: {{ error }}</p>
    </div>

    <!-- No SDG Selected Placeholder -->
    <div v-if="!currentSDG && !loading" class="text-center text-gray-600 text-lg">
      Please select an SDG to view the leaderboard.
    </div>

    <!-- Scrollable Leaderboard Table -->
    <div v-if="leaderboard.length > 0" class="overflow-x-auto">
      <div class="max-h-[800px] overflow-y-auto border border-gray-300 rounded-lg shadow-lg">
        <table class="w-full border-collapse">
          <thead class="bg-gray-100 sticky top-0">
          <tr class="text-left text-gray-700">
            <th class="p-4 border border-gray-300 text-center w-16">#</th>
            <th class="p-4 border border-gray-300">Nickname</th>
            <th class="p-4 border border-gray-300">Rank</th>
            <th class="p-4 border border-gray-300 text-center">Rank Symbol</th>
            <th class="p-4 border border-gray-300 text-center w-24">XP</th>
          </tr>
          </thead>
          <tbody class="bg-white">
          <tr
            v-for="(user, index) in visibleLeaderboard"
            :key="user.userId"
            class="hover:bg-gray-50 transition duration-200"
          >
            <!-- Rank Number -->
            <td class="p-4 border border-gray-300 text-center font-semibold text-gray-700">
              {{ index + 1 }}
            </td>

            <!-- Avatar & Nickname -->
            <td class="p-4 border border-gray-300 flex items-center space-x-4">
              <div class="relative">
                <!-- Avatar with border based on rank -->
                <div
                  :class="[
                      'w-12 h-12 rounded-full overflow-hidden border-4',
                      getAvatarFrameClass(user.rank?.tier)
                    ]"
                >
                  <img :src="generateAvatar(user.email)" alt="User Avatar" class="w-full h-full" />
                </div>
              </div>
              <span class="text-lg font-semibold text-gray-800">{{ user.nickname }}</span>
            </td>

            <!-- Rank Display (Text) -->
            <td class="p-4 border border-gray-300">
                <span
                  v-if="user.rank"
                  :class="['px-3 py-1 rounded-lg text-white text-sm font-semibold', getRankBadgeClass(user.rank?.tier)]"
                >
                  {{ user.rank.name }} (Tier {{ user.rank.tier }})
                </span>
              <span v-else class="text-gray-400">No Rank</span>
            </td>

            <!-- Rank Symbol (Chevron Icons) -->
            <td class="p-4 border border-gray-300 text-center">
              <!-- Tier 1: Single Chevron -->
              <Icon
                v-if="user.rank?.tier === 1"
                name="line-md:chevron-up"
                class="text-gray-700 w-6 h-6"
              />

              <!-- Tier 2: Double Chevron -->
              <Icon
                v-else-if="user.rank?.tier === 2"
                name="line-md:chevron-double-up"
                class="text-gray-700 w-6 h-6"
              />

              <!-- Tier 3: Triple Chevron -->
              <Icon
                v-else-if="user.rank?.tier === 3"
                name="line-md:chevron-triple-up"
                class="text-yellow-500 w-6 h-6"
              />

              <!-- No Rank (Default) -->
              <Icon v-else name="line-md:minus" class="text-gray-400 w-6 h-6" />
            </td>



            <!-- XP Display -->
            <td class="p-4 border border-gray-300 text-center text-lg font-semibold text-gray-800">
              {{ user.sdgXp }}
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Load More Button -->
      <div v-if="visibleCount < leaderboard.length" class="text-center mt-4">
        <button
          @click="loadMore"
          class="px-5 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
        >
          Load More
        </button>
      </div>
    </div>

    <!-- No Users Found -->
    <p v-else class="text-gray-600 text-center text-lg">No users found.</p>
  </div>
</template>



<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useUsersStore } from "~/stores/users";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { useXPBanksStore } from "~/stores/xpBanks";
import { useSDGsStore } from "~/stores/sdgs";
import { generateAvatar } from "~/utils/avatar";

// Stores
const userStore = useUsersStore();
const rankStore = useSDGRanksStore();
const xpBankStore = useXPBanksStore();
const sdgStore = useSDGsStore();

// Reactive State
const loading = ref(true);
const error = ref<string | null>(null);
const leaderboard = ref<
  { userId: number; nickname:string, email: string; sdgXp: number; rank?: { name: string; tier: number } }[]
>([]);
const visibleCount = ref(10); // Start with 10 players visible

// Get the currently selected SDG
const currentSDG = computed(() => {
  const sdgId = sdgStore.getSelectedSDG;
  return sdgStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Compute visible players
const visibleLeaderboard = computed(() => leaderboard.value.slice(0, visibleCount.value));

// Watch for SDG changes and update leaderboard dynamically
watch(currentSDG, async (newSDG) => {
  if (newSDG) {
    visibleCount.value = 10; // Reset visible count when SDG changes
    await updateLeaderboard();
  }
});

// Fetch users, XP, and ranks on mount
onMounted(async () => {
  await fetchData();
  if (currentSDG.value) {
    await updateLeaderboard();
  }
});

// Fetch initial data
async function fetchData() {
  try {
    loading.value = true;
    await userStore.fetchUsers();
    await xpBankStore.fetchXPBanks();
    await rankStore.fetchSDGRanks();
  } catch (err) {
    console.error("Error fetching initial data:", err);
    error.value = err.message || "Failed to load data.";
  } finally {
    loading.value = false;
  }
}
// Update leaderboard based on the selected SDG
async function updateLeaderboard() {
  if (!currentSDG.value) {
    leaderboard.value = [];
    return;
  }

  try {
    loading.value = true;
    const sdgField = `sdg${currentSDG.value.id}Xp`; // Example: "sdg1Xp" for SDG 1

    // Map users with XP for the selected SDG
    const usersWithXp = userStore.users.map((user) => {
      const xpData = xpBankStore.xpBanks.find((xp) => xp.userId === user.userId);
      const sdgXp = xpData ? xpData[sdgField] || 0 : 0;

      // ✅ Get user's ranks from `sdgRanksStore.userSDGRanks`
      const userRankData = rankStore.userSDGRanks.find((u) => u.userId === user.userId);
      const rank = userRankData?.ranks.find((r) => r.sdgGoalId === currentSDG.value.id);

      return {
        userId: user.userId,
        nickname: user.nickname,
        email: user.email,
        sdgXp: sdgXp,
        rank: rank ? { name: rank.name, tier: rank.tier } : undefined,
      };
    });

    // ✅ Sort users by XP in DESCENDING ORDER (highest XP first)
    leaderboard.value = usersWithXp.sort((a, b) => b.sdgXp - a.sdgXp);
  } catch (err) {
    console.error("Error updating leaderboard:", err);
    error.value = "Failed to update leaderboard.";
  } finally {
    loading.value = false;
  }
}



// Load more players
function loadMore() {
  visibleCount.value += 10; // Show 10 more players each time
}

// Assign avatar frames based on rank tier (0-4)
const getAvatarFrameClass = (tier?: number) => {
  switch (tier) {
    case 0:
      return "border-gray-400"; // Basic (Gray)
    case 1:
      return "border-green-500"; // Beginner (Green)
    case 2:
      return "border-blue-500"; // Intermediate (Blue)
    case 3:
      return "border-yellow-500"; // Elite (Gold)
    default:
      return "border-gray-300"; // Default
  }
};

// Assign rank badge colors based on tier
const getRankBadgeClass = (tier?: number) => {
  switch (tier) {
    case 0:
      return "bg-gray-400"; // Basic
    case 1:
      return "bg-green-500"; // Beginner
    case 2:
      return "bg-blue-500"; // Intermediate
    case 3:
      return "bg-yellow-500"; // Elite
    default:
      return "bg-gray-300"; // Default
  }
};

</script>
