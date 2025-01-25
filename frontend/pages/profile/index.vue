<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <!-- User Avatar -->
      <div class="flex justify-center mb-6">
        <img
          :src="avatarUrl"
          alt="User Avatar"
          class="w-24 h-24 rounded-full"
        />
      </div>

      <!-- User Email -->
      <h2 class="text-2xl font-bold mb-6 text-center">Welcome, {{ authStore.userProfile?.email }}</h2>

      <!-- User Roles -->
      <p>Your Roles:</p>
      <ul>
        <li v-for="role in authStore.userProfile?.roles" :key="role">
          {{ role }}
        </li>
      </ul>

      <!-- Logout Button -->
      <button
        @click="logout"
        class="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 mt-4"
      >
        Logout
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthentication } from "#imports";
import { onMounted, computed } from "vue";
import { generateAvatar } from "~/utils/avatar";

const auth = useAuthentication();
const authStore = useAuthStore();
const router = useRouter();

// Fetch user profile when the page is loaded
onMounted(async () => {
  try {
    // Fetch the user profile if a token exists
    const profile = await auth.getProfile();
    authStore.setUserProfile(profile);
  } catch (error) {
    console.error('Failed to fetch profile:', error);
    // Redirect to login if fetching the profile fails (e.g., invalid token)
    router.push('/login');
  }
});

// Generate the avatar URL based on the user's email
const avatarUrl = computed(() => {
  const email = authStore.userProfile?.email || '';
  return generateAvatar(email);
});

const logout = () => {
  auth.logout();
  authStore.clearUserProfile();
  router.push('/login');
};
</script>
