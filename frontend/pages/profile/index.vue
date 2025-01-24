<template>
  <div class="profile-container">
    <h2>Welcome, {{ user?.email }}</h2>
    <img :src="avatar" alt="User Avatar" />
    <UAvatar
      chip-color="primary"
      chip-text=""
      chip-position="top-right"
      size="sm"
      :src="avatar"
      alt="Avatar"
    />
    <p>Your Roles:</p>
    <ul>
      <li v-for="role in user?.roles" :key="role">
        {{ role }}
      </li>
    </ul>
    <UButton label="Logout" @click="logout"></UButton>
    <UButton label="Show toast" @click="toast.add({ title: 'Hello world!' })" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import useAuthentication from '~/composables/useAuthentication';
import useAvatar from '@/composables/useAvatar';

const user = ref<{ email: string; roles: string[] } | null>(null);
const router = useRouter();

// Initialize avatar
const { avatar, seed, generateAvatar } = useAvatar('');

// Fetch user profile
const fetchUserProfile = async () => {
  try {
    const authService = useAuthentication(); // Call as a function
    const profile = await authService.getProfile();
    user.value = profile;
    seed.value = profile.email; // Generate avatar based on email
  } catch (error) {
    router.push('/login'); // Redirect to login if token is invalid or expired
  }
};

// Logout
const logout = () => {
  const authService = useAuthentication(); // Call as a function
  authService.logout();
  router.push('/login');
};

// Fetch profile on mount
onMounted(fetchUserProfile);

// Toast
const toast = useToast();
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 0 auto;
}
</style>
