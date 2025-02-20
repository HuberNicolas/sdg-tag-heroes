<template>
  <div class="p-5">
    <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">
      Leaderboard - {{ currentSDG ? `SDG${currentSDG.id} - ${currentSDG.shortTitle}` : "Please select an SDG" }}
    </h1>

    <!-- Loading State -->
    <div v-if="loading" class="text-lg text-center">Loading leaderboard...</div>

    <!-- Error State -->
    <div v-if="error" class="text-red-500 text-lg text-center">
      <p>An error occurred: {{ error }}</p>
    </div>

    <!-- No SDG Selected Placeholder -->
    <div v-if="!currentSDG && !loading" class="text-center text-gray-600 text-lg">
      Please select an SDG to view the leaderboard.
    </div>

    <!-- Scrollable Leaderboard Table -->
    <div v-if="currentSDG && leaderboard.length > 0" class="overflow-x-auto">
      <div class="max-h-[800px] overflow-y-auto border border-gray-300 rounded-lg shadow-lg">
        <table class="w-full border-collapse">
          <thead class="bg-gray-100 sticky top-0">
          <tr class="text-left text-gray-700">
            <th class="p-4 border border-gray-300 text-center w-16">#</th>
            <th class="p-4 border border-gray-300">User</th>
            <th class="p-4 border border-gray-300 text-center">Rank Tier</th>
            <th class="p-4 border border-gray-300 text-center">Rank Symbol</th>
            <th class="p-4 border border-gray-300">Rank Title</th>
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
              <!-- Outer Container for Free Space -->
              <div class="relative flex items-center justify-center p-2">
                <!-- Inner Frame with SDG Color Border -->
                <div
                  v-if="user.rank?.tier !== 0"
                  :style="{ borderColor: sdgColor }"
                  :class="[
      'w-16 h-16 rounded-full flex items-center justify-center border-4',
      getBorderStyle(user.rank?.tier)
    ]"
                >
                  <!-- Avatar Inside the Frame -->
                  <div class="w-12 h-12 rounded-full overflow-hidden">
                    <img :src="generateAvatar(user.email)" alt="User Avatar" class="w-full h-full" />
                  </div>
                </div>

                <!-- Direct Avatar (No Frame) if Tier is 0 -->
                <div v-else class="w-12 h-12 rounded-full overflow-hidden">
                  <img :src="generateAvatar(user.email)" alt="User Avatar" class="w-full h-full" />
                </div>
              </div>

              <span class="text-lg font-semibold text-gray-800">{{ user.nickname }}</span>
            </td>


            <!-- Rank Tier (Number) -->
            <td class="p-4 border border-gray-300 text-center font-semibold text-gray-700">
              {{ user.rank?.tier !== undefined ? user.rank.tier : "-" }}
            </td>

            <!-- Rank Symbol (Chevron Icons) -->
            <td class="p-4 border border-gray-300 text-center">
              <Icon
                v-if="user.rank?.tier === 1"
                name="line-md:chevron-up"
                :style="{ color: sdgColor }"
                class="w-6 h-6"
              />
              <Icon
                v-else-if="user.rank?.tier === 2"
                name="line-md:chevron-double-up"
                :style="{ color: sdgColor }"
                class="w-6 h-6"
              />
              <Icon
                v-else-if="user.rank?.tier === 3"
                name="line-md:chevron-triple-up"
                :style="{ color: sdgColor }"
                class="w-6 h-6"
              />
              <Icon v-else name="line-md:minus" class="text-gray-400 w-6 h-6" />
            </td>


            <!-- Rank Title -->
            <td class="p-4 border border-gray-300 text-center whitespace-nowrap">
              <span
                v-if="user.rank"
                :style="{ backgroundColor: sdgColor }"
                class="px-3 py-1 rounded-lg text-white text-sm font-semibold"
              >
                {{ user.rank.name }}
              </span>
              <span v-else class="text-gray-400">No Rank</span>
            </td>

            <!-- XP Display -->
            <td class="p-4 border border-gray-300 text-center text-lg font-semibold text-gray-800">
              {{ Math.round(user.sdgXp) }}
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Load More Button -->
      <div v-if="visibleCount < leaderboard.length" class="text-center mt-4">
        <UButton
          @click="loadMore"
          :color="'primary'"
          :variant="'solid'"
          class="px-5 py-2"
        >
          Load More
        </UButton>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useUsersStore } from "~/stores/users";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { useXPBanksStore } from "~/stores/xpBanks";
import { useSDGsStore } from "~/stores/sdgs";
import { useGameStore } from "~/stores/game";
import { generateAvatar } from "~/utils/avatar";

// Stores
const userStore = useUsersStore();
const rankStore = useSDGRanksStore();
const xpBankStore = useXPBanksStore();
const sdgStore = useSDGsStore();
const gameStore = useGameStore();

// Reactive State
const loading = ref(true);
const error = ref<string | null>(null);
const leaderboard = ref<
  { userId: number; nickname: string, email: string; sdgXp: number; rank?: { name: string; tier: number } }[]
>([]);
const visibleCount = ref(10); // Start with 10 players visible

// Get the currently selected SDG
const currentSDG = computed(() => {
  const sdgId = gameStore.getSDG;
  return sdgStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Computed property to get the color of the selected SDG
const sdgColor = computed(() => {
  return currentSDG.value ? sdgStore.getColorBySDG(currentSDG.value.id) : "#A0A0A0"; // Default gray if no SDG
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
    await rankStore.fetchSDGRanksForUsers();
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
        rank: rank ? { name: rank.name, tier: rank.tier } : undefined
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

// Function to return different border styles based on rank tier
const getBorderStyle = (tier?: number) => {
  switch (tier) {
    case 0:
      return ""; // Dashed border for beginners
    case 1:
      return "border-double"; // Solid border for intermediate
    case 2:
      return "border-dashed"; // Double border for advanced
    case 3:
      return "border-solid"; // Thick double border for elite

    default:
      return "border-solid"; // Default to solid if no rank
  }
};

</script>
