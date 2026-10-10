<template>
  <div class="min-h-full flex items-center justify-center p-6">
    <div class="relative bg-surface/80 backdrop-blur-xl border border-line p-8 rounded-[18px] shadow-panel w-full max-w-md">
      <p class="kicker text-center mb-4">// profile</p>
      <!-- User Avatar -->
      <div class="flex justify-center mb-6">
        <img
          :src="avatarUrl"
          alt="User Avatar"
          class="w-24 h-24 rounded-full ring-2 ring-accent/50 ring-offset-4 ring-offset-surface"
        >
      </div>

      <!-- User Email -->
      <h2 class="text-xl font-bold tracking-tight mb-6 text-center break-all">Welcome, {{ authStore.userProfile?.email }}</h2>

      <!-- User Roles -->
      <p class="font-mono text-xs text-fg-dim">Your Roles:</p>
      <ul class="mt-2 flex flex-wrap gap-2">
        <li v-for="role in authStore.userProfile?.roles" :key="role" class="stat-pill">
          <Icon name="mdi-shield-account-outline" class="text-accent" />{{ role }}
        </li>
      </ul>

      <!-- Logout Button -->
      <button
        class="w-full mt-6 rounded-[10px] border border-hero-red/40 bg-hero-red/10 py-2.5 px-4 font-mono text-sm text-hero-red transition hover:bg-hero-red/20 focus:outline-none focus:ring-4 focus:ring-hero-red/20"
        @click="logout"
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
