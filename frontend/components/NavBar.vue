<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from "~/stores/user"; // Import SDG store
import UseAuth from '~/composables/useAuth';
import useAvatar from '@/composables/useAvatar';
import IconSDGXP from '~/assets/average_sdg_predction_glyph.svg';
import IconSDG1XP from '~/assets/sdg_01_glyph.svg';
import IconSDG2XP from '~/assets/sdg_02_glyph.svg';
import IconSDG3XP from '~/assets/sdg_03_glyph.svg';
import IconSDG4XP from '~/assets/sdg_04_glyph.svg';
import IconSDG5XP from '~/assets/sdg_05_glyph.svg';
import IconSDG6XP from '~/assets/sdg_06_glyph.svg';
import IconSDG7XP from '~/assets/sdg_07_glyph.svg';
import IconSDG8XP from '~/assets/sdg_08_glyph.svg';
import IconSDG9XP from '~/assets/sdg_09_glyph.svg';
import IconSDG10XP from '~/assets/sdg_10_glyph.svg';
import IconSDG11XP from '~/assets/sdg_11_glyph.svg';
import IconSDG12XP from '~/assets/sdg_12_glyph.svg';
import IconSDG13XP from '~/assets/sdg_13_glyph.svg';
import IconSDG14XP from '~/assets/sdg_14_glyph.svg';
import IconSDG15XP from '~/assets/sdg_15_glyph.svg';
import IconSDG16XP from '~/assets/sdg_16_glyph.svg';
import IconSDG17XP from '~/assets/sdg_17_glyph.svg';
import type { SDGXPBankResponse } from "~/types/sdgXPBank";

const sdgIcons = {
  sdg_1: IconSDG1XP,
  sdg_2: IconSDG2XP,
  sdg_3: IconSDG3XP,
  sdg_4: IconSDG4XP,
  sdg_5: IconSDG5XP,
  sdg_6: IconSDG6XP,
  sdg_7: IconSDG7XP,
  sdg_8: IconSDG8XP,
  sdg_9: IconSDG9XP,
  sdg_10: IconSDG10XP,
  sdg_11: IconSDG11XP,
  sdg_12: IconSDG12XP,
  sdg_13: IconSDG13XP,
  sdg_14: IconSDG14XP,
  sdg_15: IconSDG15XP,
  sdg_16: IconSDG16XP,
  sdg_17: IconSDG17XP,
};



// State for user and avatar
const user = ref<{ email: string } | null>(null);
const avatarSrc = ref<string | null>(null);
const loading = ref(true); // Loading state
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
      const [coins, xpData] = await Promise.all([
        userStore.fetchSDGCoins(user.value.user_id),
        userStore.fetchSDGXP(user.value.user_id)
      ]);

      // Update links with SDG data
      updateLinks(coins, xpData);
    }

  } catch (error) {
    console.error("Error fetching user profile:", error);
  } finally {
    loading.value = false; // Set loading to false once complete
  }
};
const updateLinks = (coins: number, xpData: SDGXPBankResponse) => {
  const { total_xp, ...otherFields } = xpData;

  // Extract SDG XP values dynamically
  const sdgXPs = Object.entries(otherFields)
    .filter(([key]) => key.startsWith('sdg_') && key.endsWith('_xp')) // Match SDG keys
    .map(([key, xp]) => {
      const normalizedKey = key.replace('_xp', ''); // Remove `_xp` suffix
      return {
        sdg: normalizedKey,
        xp: xp as number, // Ensure it's treated as a number
        customIconSrc: sdgIcons[normalizedKey] || null,
      };
    });

  // Sort by XP in descending order and take the top 3
  const top3SDGs = sdgXPs
    .sort((a, b) => b.xp - a.xp)
    .slice(0, 3)
    .map((sdgData, index) => ({
      label: `${index + 1}. ${sdgData.sdg.replace('sdg_', 'SDG ')}: ${sdgData.xp.toFixed(2)} XP`,
      component: sdgData.sdg,
    }));

  console.log('Top 3 SDGs:', top3SDGs);

  // Populate links
  links.value = [
    [
      {
        label: 'Home',
        icon: 'i-heroicons-home',
        to: '/',
      },
      {
        label: `SDG XP: ${total_xp.toFixed(2)}`,
        customIcon: true, // Mark this for a custom slot
      },
      {
        label: `SDG Coins: ${coins.toFixed(2)}`,
        icon: 'i-heroicons-currency-dollar',
      },
    ],
    top3SDGs, // Use top 3 SDG XPs
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

  console.log('Final links:', links.value);
};


// Watch for changes to `avatarSrc` and update links
onMounted(async () => {
  await fetchUserProfile();
});
</script>

<template>
  <!-- Show loading state until links are ready -->
  <div v-if="loading" class="flex justify-center items-center h-32">
    <span class="text-gray-500">Loading...</span>
  </div>

  <!-- Render content once links are ready -->
  <div v-else class="flex flex-col items-center p-4 space-y-6 bg-gray-50 dark:bg-gray-900">
    <!-- Overall SDG XP -->
    <div v-if="links[0]?.[1]" class="flex items-center space-x-4">
      <IconSDGXP class="w-12 h-12 rotate-45" :fontControlled="false" />
      <span class="text-lg font-semibold text-gray-700 dark:text-gray-200">
        {{ links[0][1]?.label.split(': ')[1] || '0' }}
      </span>
    </div>

    <!-- Top 3 SDGs -->
    <div v-if="links[1]" class="grid grid-cols-3 gap-4">
      <div
        v-for="(link, index) in links[1]"
        :key="index"
        class="flex flex-col items-center space-y-2"
      >
        <!-- Switch to decide which component to render -->
        <div class="w-12 h-12">
          <IconSDG1XP class="w-12 h-12 rotate-45" :fontControlled="false" v-if="link.component === 'sdg_1'" />
          <IconSDG2XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_2'" />
          <IconSDG3XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_3'" />
          <IconSDG4XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_4'" />
          <IconSDG5XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_5'" />
          <IconSDG6XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_6'" />
          <IconSDG7XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_7'" />
          <IconSDG8XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_8'" />
          <IconSDG9XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_9'" />
          <IconSDG10XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_10'" />
          <IconSDG11XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_11'" />
          <IconSDG12XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_12'" />
          <IconSDG13XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_13'" />
          <IconSDG14XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_14'" />
          <IconSDG15XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_15'" />
          <IconSDG16XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_16'" />
          <IconSDG17XP class="w-12 h-12 rotate-45" :fontControlled="false" v-else-if="link.component === 'sdg_17'" />
        </div>

        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
          {{ link.label }}
        </span>
      </div>
    </div>


    <!-- Avatar -->
    <div v-if="links[2]?.[0]?.avatar" class="flex items-center space-x-4">
      <img
        :src="links[2][0].avatar.src"
        :alt="links[2][0].avatar.alt"
        class="w-12 h-12 rounded-full border-2 border-primary"
      />
      <span class="text-gray-700 dark:text-gray-200">My Profile</span>
    </div>
  </div>
</template>


