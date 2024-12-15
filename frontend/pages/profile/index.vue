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
import UseAuth from '~/composables/useAuth';
import useAvatar from '@/composables/useAvatar';

const user = ref<{ email: string, role: string } | null>(null);
const router = useRouter();

// Initialize avatar with null or an empty string
const { avatar, seed, generateAvatar } = useAvatar('');

const fetchUserProfile = async () => {
  try {
    const authService = new UseAuth();
    user.value = await authService.getProfile();
    seed.value = user.value?.email;
  } catch (error) {
    router.push('/login');  // Redirect to login if token is invalid or expired
  }
};

watch(user, (newValue) => {
  // Regenerate avatar whenever user data changes
  if (newValue?.email) {
    generateAvatar(newValue.email);
  }
});

const logout = () => {
  const authService = new UseAuth();
  authService.logout();
  router.push('/login');
};
definePageMeta({
  layout: 'user'
})
onMounted(fetchUserProfile);


const toast = useToast()
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 0 auto;
}
</style>
