<script setup lang="ts">
import { ref, onMounted } from 'vue';
import UseAuth from '~/composables/useAuth';
import useAvatar from '@/composables/useAvatar';

// Define links for the navigation bar (without the Profile link)
const links = [
  [
    {
      label: 'Home',
      icon: 'i-heroicons-home',
    }
  ],
  [
    {
      label: 'Help',
      icon: 'i-heroicons-question-mark-circle'
    }
  ]
];

// Handle user authentication and avatar
const user = ref<{ email: string, role: string } | null>(null);
const { avatar, seed, generateAvatar } = useAvatar('');
const authService = new UseAuth();
const isLoggedIn = ref(false);

const fetchUserProfile = async () => {
  try {
    // Fetch the user's profile
    user.value = await authService.getProfile();
    isLoggedIn.value = true;
    seed.value = user.value?.email;
    if (user.value?.email) {
      // Generate the avatar using the email as a seed
      generateAvatar(user.value.email);
    }
  } catch (error) {
    // If the user is not authenticated, set isLoggedIn to false
    isLoggedIn.value = false;
  }
};

// Fetch the user profile when the component is mounted
onMounted(fetchUserProfile);
</script>

<template>
  <div class="flex items-center border-b border-gray-200 dark:border-gray-800">
    <!-- Render the navigation links -->
    <UHorizontalNavigation :links="links" class="flex-grow" />

    <!-- Separate Avatar Section -->
    <div class="ml-4">
      <template v-if="isLoggedIn">
        <!-- Show the user's avatar if logged in -->
        <UAvatar size="sm" :src="avatar" alt="User Avatar" />
      </template>
      <template v-else>
        <!-- Show a placeholder icon if not logged in -->
        <i class="i-heroicons-user-circle"></i>
      </template>
    </div>
  </div>
</template>
