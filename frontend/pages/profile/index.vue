<template>
  <div class="profile-container">
    <h2>Welcome, {{ user?.email }}</h2>
    <p>Your role: {{ user?.role }}</p>
    <button @click="logout">Logout</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/authService';

const user = ref<{ email: string, role: string } | null>(null);
const router = useRouter();

const fetchUserProfile = async () => {
  try {
    const authService = new AuthService();
    user.value = await authService.getProfile();
  } catch (error) {
    router.push('/login');  // Redirect to login if token is invalid or expired
  }
};

const logout = () => {
  const authService = new AuthService();
  authService.logout();
  router.push('/login');
};

onMounted(fetchUserProfile);
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 0 auto;
}
</style>
