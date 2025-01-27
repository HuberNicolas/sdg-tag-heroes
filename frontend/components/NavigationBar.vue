<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUsersStore } from '~/stores/users';
import { useXPBanksStore } from '~/stores/xpBanks';
import { useCoinWalletsStore } from '~/stores/coinWallets';
import { generateAvatar } from '~/utils/avatar'; // Import the synchronous generateAvatar funct
import { sdgGlyphs } from '~/constants/constants';

// Pinia stores
const userStore = useUsersStore();
const banksStore = useXPBanksStore();
const walletsStore = useCoinWalletsStore();

// State
const loading = ref(true);
const links = ref<Array<any>>([]);


// Fetch all required data
const fetchData = async () => {
  try {
    await Promise.all([
      userStore.fetchPersonalUser(),
      walletsStore.fetchPersonalSDGCoinWallet(),
      banksStore.fetchPersonalXPBank(),
    ]);

    const user = userStore.getCurrentUser;
    const userWallet = walletsStore.getUserSDGCoinWallet;
    const userBank = banksStore.getUserXPBank;

    // Update links with fetched data
    updateLinks(userWallet?.totalCoins || 0, userBank || { totalXp: 0 });
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
  console.log(totalXp, sdgXpFields);

  // Extract and sort top 3 SDGs by XP
  const top3SDGs = Object.entries(sdgXpFields)
    .filter(([key]) => key.startsWith('sdg') && key.endsWith('Xp'))
    .map(([key, xp]) => ({
      sdg: key.replace('_xp', ''),
      xp: xp as number,
    }))
    .sort((a, b) => b.xp - a.xp)
    .slice(0, 3)
    .map((sdgData) => ({
      label: `${sdgData.sdg.replace('sdg', 'SDG ')}: ${sdgData.xp.toFixed(0)}`,
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
    ...top3SDGs
  ];
};

// Fetch data on component mount
onMounted(fetchData);
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
        <div class="user-avatar">
          <!-- Generate avatar directly in the template -->
          <UAvatar
            v-if="userStore.getCurrentUser?.email"
            chip-color="primary"
            chip-text=""
            chip-position="top-right"
            size="lg"
            :src="generateAvatar(userStore.getCurrentUser.email)"
            alt="Avatar"
          />
          <!-- Fallback if no email is available -->
          <div v-else class="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
            <span class="text-gray-500">No Avatar</span>
          </div>
        </div>
      </NuxtLink>
    </div>
  </nav>
</template>
