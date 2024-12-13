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
      label: `${sdgData.sdg.replace('sdg_', 'SDG ')}: ${sdgData.xp.toFixed(0)} XP`,
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
        label: `SDG XP: ${total_xp.toFixed(0)}`,
        customIcon: true,
      },
      {
        label: `SDG Coins: ${coins.toFixed(0)}`,
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
  <div v-if="loading" class="flex justify-center items-center">
    <span class="text-gray-500">Loading...</span>
  </div>

  <!-- Render content once links are ready -->
  <nav v-else class="w-full bg-gray-100 dark:bg-gray-800 shadow-md">
    <div class="max-w-7xl mx-auto flex items-center justify-between px-4 py-2">
      <!-- Left Section: Home and Overall SDG XP -->
      <div class="flex items-center space-x-6">
        <!-- Home Link -->
        <NuxtLink to="/">
          <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200">Home</span>
          </div>
        </NuxtLink>

        <!-- Overall SDG XP -->
        <NuxtLink :to="{ name: 'worlds' }">
          <div class="flex items-center space-x-2">
            <IconSDGXP class="w-12 h-12 rotate-45 text-gray-700 dark:text-gray-300" :fontControlled="false" />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200">
              {{ links[0][1]?.label || '0' }}
            </span>
          </div>
        </NuxtLink>
        <!-- Overall Coins XP -->
        <div class="flex items-center space-x-2">
          <Icon name="heroicons-currency-dollar" style="color: black" />
          <span class="text-sm font-medium text-gray-700 dark:text-gray-200">
            {{ links[0][2]?.label || '0' }}
          </span>
        </div>
      </div>

      <!-- Center Section: Top 3 SDGs -->
      <div class="flex items-center space-x-4">
          <div
            v-for="(link, index) in links[1]"
            :key="index"
            class="flex flex-col items-center space-y-1"
          >
            <NuxtLink :to="{ name: 'worlds-id', params: { id: index+1 } }">
            <!-- Dynamic SDG Icon -->
            <div class="w-12 h-12 flex items-center justify-center">
              <IconSDG1XP v-if="link.component === 'sdg_1'" class="w-12 h-12 rotate-45" :fontControlled="false"/>
              <IconSDG2XP v-else-if="link.component === 'sdg_2'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG3XP v-else-if="link.component === 'sdg_3'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG4XP v-else-if="link.component === 'sdg_4'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG5XP v-else-if="link.component === 'sdg_5'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG6XP v-else-if="link.component === 'sdg_6'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG7XP v-else-if="link.component === 'sdg_7'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG8XP v-else-if="link.component === 'sdg_8'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG9XP v-else-if="link.component === 'sdg_9'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG10XP v-else-if="link.component === 'sdg_10'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG11XP v-else-if="link.component === 'sdg_11'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG12XP v-else-if="link.component === 'sdg_12'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG13XP v-else-if="link.component === 'sdg_13'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG14XP v-else-if="link.component === 'sdg_14'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG15XP v-else-if="link.component === 'sdg_15'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG16XP v-else-if="link.component === 'sdg_16'" class="w-12 h-12 rotate-45" :fontControlled="false" />
              <IconSDG17XP v-else-if="link.component === 'sdg_17'" class="w-12 h-12 rotate-45" :fontControlled="false" />
            </div>

            <!-- Label -->
            <span class="text-xs font-medium text-gray-600 dark:text-gray-400">
              {{ link.label }}
            </span>
            </NuxtLink>
          </div>
      </div>

      <!-- Right Section: Avatar -->
      <NuxtLink :to="{ name: 'profile' }">
        <div v-if="links[2]?.[0]?.avatar" class="flex items-center space-x-2">
          <img
            :src="links[2][0].avatar.src"
            :alt="links[2][0].avatar.alt"
            class="w-10 h-10 rounded-full border-2 border-primary"
          />
          <span class="text-sm font-medium text-gray-700 dark:text-gray-200">Profile</span>
        </div>
      </NuxtLink>
    </div>
  </nav>
</template>



