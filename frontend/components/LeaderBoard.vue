<template>
  <div>
    <div class="users-page">
      <h1 class="text-2xl font-bold mb-4">SDG XP Leaderboard</h1>

      <!-- Loading state -->
      <div v-if="loading" class="text-blue-500">
        Loading leaderboard...
      </div>

      <!-- Error state -->
      <div v-if="error" class="text-red-500">
        <p>An error occurred: {{ error }}</p>
      </div>




      <div v-else>
        <!-- Legend -->
        <div class="mb-6 p-4 border rounded-lg bg-white shadow-sm">
          <h2 class="text-lg font-semibold mb-2">Leaderboard Legend</h2>
          <p class="text-sm text-gray-600 mb-4">Users are ranked based on their SDG XP. Higher XP reflects greater engagement and achievements in the SDG activities.</p>
          <div class="flex flex-wrap gap-4">
            <div class="flex items-center border border-gray-200 rounded-lg p-2 bg-[#b9f2ff]/10">
              <span class="inline-block w-5 h-5 border-3 rounded-full border-[#b9f2ff] mr-2"></span>
              <span class="text-sm font-medium text-gray-700">Diamond: > 500 XP</span>
            </div>
            <div class="flex items-center border border-gray-200 rounded-lg p-2 bg-[#e5e4e2]/10">
              <span class="inline-block w-5 h-5 border-3 rounded-full border-[#e5e4e2] mr-2"></span>
              <span class="text-sm font-medium text-gray-700">Platinum: > 200 XP</span>
            </div>
            <div class="flex items-center border border-gray-200 rounded-lg p-2 bg-[#ffd700]/10">
              <span class="inline-block w-5 h-5 border-3 rounded-full border-[#ffd700] mr-2"></span>
              <span class="text-sm font-medium text-gray-700">Gold: > 100 XP</span>
            </div>
            <div class="flex items-center border border-gray-200 rounded-lg p-2 bg-[#c0c0c0]/10">
              <span class="inline-block w-5 h-5 border-3 rounded-full border-[#c0c0c0] mr-2"></span>
              <span class="text-sm font-medium text-gray-700">Silver: > 50 XP</span>
            </div>
            <div class="flex items-center border border-gray-200 rounded-lg p-2 bg-[#cd7f32]/10">
              <span class="inline-block w-5 h-5 border-3 rounded-full border-[#cd7f32] mr-2"></span>
              <span class="text-sm font-medium text-gray-700">Bronze: > 10 XP</span>
            </div>
            <div class="flex items-center border border-gray-200 rounded-lg p-2 bg-gray-100">
              <span class="inline-block w-5 h-5 border-3 rounded-full border-gray-500 mr-2"></span>
              <span class="text-sm font-medium text-gray-700">No Frame: ≤ 10 XP</span>
            </div>
          </div>
        </div>


        <!-- Leaderboard -->
        <div class="overflow-y-auto max-h-96">
        <table class="min-w-full bg-white border border-gray-200 rounded-lg shadow-lg">
          <thead class="bg-gray-100">
          <tr>
            <th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Rank</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-gray-500">User</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Name</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-gray-500">XP</th>
          </tr>
          </thead>
          <tbody>
          <tr
            v-for="(user, index) in leaderboard"
            :key="user.user_id"
            :class="{'highlighted-user': user.user_id === loggedInUserId}"
            class="border-t hover:bg-gray-50"
          >
            <td class="px-6 py-4 text-sm font-medium text-gray-700">{{ index + 1 }}</td>
            <td class="px-6 py-4 text-sm text-gray-700">
              <router-link :to="`/users/${user.user_id}`" class="text-blue-500 hover:underline">
                <!-- {{ user.email }} -->
                <div :class="['user-avatar', getAvatarFrameClass(user.sdg_xp)]">
                  <!-- Generate and display the avatar -->
                  <UAvatar
                    chip-color="primary"
                    chip-text=""
                    chip-position="top-right"
                    size="sm"
                    :src="generateUserAvatar(user.email)"
                    alt="Avatar"
                  />
                </div>
              </router-link>
            </td>
            <td class="px-6 py-4 text-sm text-gray-700">{{ user.email }}</td>
            <td class="px-6 py-4 text-sm text-gray-700">{{ user.sdg_xp }}</td>
          </tr>
          </tbody>
        </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { ref, onMounted } from "vue";
import UseAuth from "~/composables/useAuth";

// Route and router setup
const route = useRoute();
const router = useRouter();

const sdgId = parseInt(route.params.id as string, 10);

// State variables
const leaderboard = ref([]);
const loading = ref(true);
const error = ref<string | null>(null);
const loggedInUserId = ref<number | null>(null); // Store logged-in user ID

// Import useAvatar composable
const { generateAvatar } = useAvatar();

// Function to generate avatars based on email
const generateUserAvatar = (email: string) => {
  return generateAvatar({ seed: email, size: 64 }).toDataUri();
};

// Function to determine the frame class based on XP
const getAvatarFrameClass = (xp: number) => {
  if (xp > 500) return "frame-diamond";
  if (xp > 200) return "frame-platinum";
  if (xp > 100) return "frame-gold";
  if (xp > 50) return "frame-silver";
  if (xp > 10) return "frame-bronze";
  return "frame-none"; // Default frame if XP is <= 10
};

// Fetch SDG XP leaderboard on mount
onMounted(async () => {
  const config = useRuntimeConfig();
  const apiUrl = config.public.apiUrl;

  try {
    const authService = new UseAuth();
    const profile = await authService.getProfile(); // Fetch logged-in user's profile
    loggedInUserId.value = profile?.user_id; // Store the logged-in user's ID


    const response = await $fetch(`${apiUrl}users/banks`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    });

    console.log("Raw API Response:", response);
    const sdgField = `sdg_${sdgId}_xp`;


    // Filter out users with 0 XP for the specific SDG and sort by XP
    leaderboard.value = response.items
      .filter((bank: any) => bank[sdgField] > 0)
      .map((bank: any) => ({
        user_id: bank.user_id,
        email: `User ${bank.user_id}`, // Replace this with an actual email if available
        sdg_xp: bank[sdgField],
      }))
      .sort((a: any, b: any) => b.sdg_xp - a.sdg_xp);

    console.log("Filtered and Sorted Leaderboard:", leaderboard.value);
  } catch (err: any) {
    console.error("Error fetching SDG XP leaderboard:", err);
    error.value = err.message || "Failed to load leaderboard.";
  } finally {
    loading.value = false;
  }


});
</script>

<style scoped>
.users-page {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.user-avatar {
  display: inline-block;
  padding: 8px; /* Space for the frame */
}

/* Frames based on XP */
.frame-bronze {
  border: 3px solid #cd7f32; /* Bronze color */
}

.frame-silver {
  border: 3px solid #c0c0c0; /* Silver color */
}

.frame-gold {
  border: 3px solid #ffd700; /* Gold color */
}

.frame-platinum {
  border: 3px solid #e5e4e2; /* Platinum color */
}

.frame-diamond {
  border: 3px solid #b9f2ff; /* Diamond color */
}

.frame-none {
  border: 3px dotted #000000; /* No frame */
}

.highlighted-user {
  background-color: #f0f8ff; /* Light blue background */
  font-weight: bold; /* Bold text */
}
</style>
