<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from "~/stores/user"; // Import SDG store
import UseAuth from '~/composables/useAuth';
import useAvatar from '@/composables/useAvatar';
import IconSDGXP from '~/assets/average_sdg_predction_glyph.svg';

// State for user and avatar
const user = ref<{ email: string } | null>(null);
const avatarSrc = ref<string | null>(null);
const links = ref([]); // Reactive links array

const userStore = useUserStore();

// Initialize avatar generator
const { generateAvatar } = useAvatar();

// Fetch user profile and generate avatar
const fetchUserProfile = async () => {
  try {
    const authService = new UseAuth();
    user.value = await authService.getProfile(); // Fetch user profile (e.g., email)
    if (user.value?.email) {
      avatarSrc.value = generateAvatar({ seed: user.value.email, size: 64 }).toDataUri();
    }

    // Fetch SDG Coins and XP
    if (user.value?.user_id) {
      const [coins, xp] = await Promise.all([
        userStore.fetchSDGCoins(user.value.user_id),
        userStore.fetchSDGXP(user.value.user_id)
      ]);

    // Update links with SDG data
      updateLinks(coins, xp);
    }

  } catch (error) {
    console.error("Error fetching user profile:", error);
  }
};

// Update links dynamically
const updateLinks = (coins: number, xp: number) => {
  links.value = [
    [
      {
        label: 'Home',
        icon: 'i-heroicons-home',
        to: '/',
      },
      {
        label: `SDG XP: ${xp.toFixed(2)}`,
        customIcon: true // Mark this for a custom slot
      },
      {
        label: `SDG Coins: ${coins.toFixed(2)}`,
        icon: "i-heroicons-currency-dollar"
      },
    ],
    [
      {
        label: '',
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
    :links="links"
    class="border-b border-gray-200 dark:border-gray-800"
  >
    <!-- Use slot to customize the customIcon -->
    <template #icon="{ link }">
      <IconSDGXP
        v-if="link.customIcon"
        class="w-12 h-12 rotate-45"
        :fontControlled="false"
      />
    </template>
  </UHorizontalNavigation>
</template>
