<script setup lang="ts">
import { ref, onMounted } from 'vue';
import UseAuth from '~/composables/useAuth';
import useAvatar from '@/composables/useAvatar';

// State for user and avatar
const user = ref<{ email: string } | null>(null);
const avatarSrc = ref<string>('');

// Initialize avatar generator
const { generateAvatar } = useAvatar();

// Fetch user profile and generate avatar
const fetchUserProfile = async () => {
  try {
    const authService = new UseAuth();
    user.value = await authService.getProfile(); // Fetch user profile (e.g., email)

    if (user.value?.email) {
      const generatedAvatar = generateAvatar({ seed: user.value.email, size: 64 }).toDataUri();
      console.log("Generated Avatar (Base64):", generatedAvatar);
      avatarSrc.value = generatedAvatar; // Assign generated avatar
    }
  } catch (error) {
    console.error("Error fetching user profile:", error);
  }
};

// Navigation links
const links = ref([]); // Reactive links array

// Update links dynamically after fetching avatar
const updateLinks = () => {
  links.value = [
    [
      {
        label: 'Home',
        icon: 'i-heroicons-home',
        to: '/getting-started/installation',
      },
      {
        label: 'Horizontal Navigation',
        icon: 'i-heroicons-chart-bar',
        to: '/components/horizontal-navigation',
      },
      {
        label: 'Commands',
        icon: 'i-heroicons-command-line',
        to: '/components/command-palette',
      },
      {
        label: 'Publications',
        icon: 'i-heroicons-document-duplicate',
        to: '/publications',
      },
    ],
    [
      {
        label: 'Profile',
        avatar: {
          src: avatarSrc.value, // Dynamically bind the avatar src
          size: 'sm',
          alt: 'User Avatar',
          chipColor: 'primary',
          chipText: '',
          chipPosition: 'top-right',
        },
        to: '/profile',
      },
    ],
  ];
};

// Watch for changes to `avatarSrc` and update links
onMounted(async () => {
  await fetchUserProfile();
  updateLinks(); // Update links after avatar is generated
});
</script>

<template>
  <UHorizontalNavigation
    v-if="links.length > 0"
    :links="links"
    class="border-b border-gray-200 dark:border-gray-800"
  />
</template>
