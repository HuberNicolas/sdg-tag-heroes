<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUsersStore } from '~/stores/users';
import { useXPBanksStore } from '~/stores/xpBanks';
import { useCoinWalletsStore } from '~/stores/coinWallets';
import useAvatar from '~/composables/useAvatar';
import { sdgGlyphs } from '~/constants/constants';

// Pinia stores
const userStore = useUsersStore();
const xpBanksStore = useXPBanksStore();
const walletsStore = useCoinWalletsStore();

// State
const loading = ref(true);
const avatarSrc = ref<string | null>(null);
const links = ref<Array<any>>([]);

const { generateAvatar } = useAvatar();

// Fetch user data
const fetchUserData = async () => {
  try {
    const [user, coins, xpBank] = await Promise.all([
      userStore.fetchPersonalUser(),
      walletsStore.fetchPersonalSDGCoinWallet(),
      xpBanksStore.fetchPersonalXPBank(),
    ]);
    console.log(user, coins, xpBank);

    if (user?.email) {
      avatarSrc.value = generateAvatar({ seed: user.email, size: 64 }).toDataUri();
    }

    updateLinks(coins.totalCoins, xpBank);
  } catch (error) {
    console.error('Error fetching user data:', error);
    updateLinks(0, { totalXp: 0 }); // Fallback values
  } finally {
    loading.value = false;
  }
};

// Update links with user data
const updateLinks = (coins: number, xpData: any) => {
  const { totalXp, ...sdgXpFields } = xpData;

  // Log XP data for debugging
  console.log('XP Data:', xpData);

  // Extract and sort top 3 SDGs by XP
  const top3SDGs = Object.entries(sdgXpFields)
    .filter(([key]) => key.startsWith('sdg_') && key.endsWith('_xp'))
    .map(([key, xp]) => ({
      sdg: key.replace('_xp', ''),
      xp: xp as number,
    }))
    .sort((a, b) => b.xp - a.xp)
    .slice(0, 3)
    .map((sdgData) => ({
      label: `${sdgData.sdg.replace('sdg_', 'SDG ')}: ${sdgData.xp.toFixed(0)} XP`,
      icon: sdgGlyphs[sdgData.sdg],
    }));

  // Populate links
  links.value = [
    {
      label: 'Worlds',
      icon: 'i-heroicons-globe-alt',
      to: '/worlds',
    },
    {
      label: `SDG XP: ${totalXp.toFixed(0)}`,
      icon: sdgGlyphs.sdg_xp,
    },
    {
      label: `SDG Coins: ${coins.toFixed(0)}`,
      icon: 'i-heroicons-currency-dollar',
    },
    ...top3SDGs,
    {
      label: 'Profile',
      avatar: avatarSrc.value,
      to: '/profile',
    },
  ];
};

onMounted(fetchUserData);
</script>

<template>
  <nav class="w-full bg-white shadow-md dark:bg-gray-800">
    <div v-if="loading" class="flex justify-center items-center h-16">
      <span class="text-gray-500">Loading...</span>
    </div>

    <div v-else class="max-w-7xl mx-auto flex justify-between items-center px-4 py-3">
      <!-- Left Section: Links -->
      <div class="flex items-center space-x-6">
        <NuxtLink
          v-for="(link, index) in links.slice(0, 3)"
          :key="index"
          :to="link.to"
          class="flex items-center space-x-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-blue-500"
        >
          <component :is="link.icon" class="w-5 h-5" />
          <span>{{ link.label }}</span>
        </NuxtLink>
      </div>

      <!-- Center Section: Top 3 SDGs -->
      <div class="flex items-center space-x-4">
        <NuxtLink
          v-for="(link, index) in links.slice(3, 6)"
          :key="index"
          :to="`/worlds/${index + 1}`"
          class="flex flex-col items-center space-y-1"
        >
          <component :is="link.icon" class="w-8 h-8" />
          <span class="text-xs font-medium text-gray-600 dark:text-gray-400">
            {{ link.label }}
          </span>
        </NuxtLink>
      </div>

      <!-- Right Section: Avatar -->
      <NuxtLink to="/profile" class="flex items-center space-x-2">
        <img
          v-if="links[6]?.avatar"
          :src="links[6].avatar"
          alt="User Avatar"
          class="w-10 h-10 rounded-full border-2 border-primary"
        />
        <span class="text-sm font-medium text-gray-700 dark:text-gray-200">Profile</span>
      </NuxtLink>
    </div>
  </nav>
</template>
