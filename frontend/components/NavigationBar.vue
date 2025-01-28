<template>
  <nav class="w-full bg-white shadow-md dark:bg-gray-800">
    <div v-if="loading" class="flex justify-center items-center">
      <span class="text-gray-500">Loading...</span>
    </div>

    <div v-else class="max-w-7xl mx-auto flex justify-between items-center px-1 py-1">
      <!-- Left Section: Links -->
      <div class="flex items-center space-x-6">
        <NuxtLink
          v-for="(link, index) in links.slice(0, 3)"
          :key="index"
          :to="link.to || '#'"
          class="flex items-center space-x-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-blue-500"
        >
          <component :is="link.icon" class="w-5 h-5" v-if="typeof link.icon === 'string'" />
          <component :is="link.icon" v-else class="w-5 h-5" />
          <span>{{ link.label }}</span>
        </NuxtLink>
      </div>

      <!-- Center Section: Top 3 SDGs -->
      <div class="flex items-center space-x-4">
        <div>Top SDGs</div>
        <div
          v-for="(link, index) in links.slice(3)"
          :key="index"
          class="flex flex-col items-center space-y-1"
        >
          <NuxtLink :to="{ name: 'worlds-id', params: { id: link.to } }">
            <!-- Dynamic SDG Icon -->
            <!-- Title -->
            <div class="w-8 h-8 flex items-center justify-center">
              <img
                v-if="link.icon"
                :src="`data:image/svg+xml;base64,${link.icon}`"
                :alt="`SDG ${index + 1} Icon`"
                class="w-full h-full object-contain"
              />
            </div>

            <!-- Label -->
            <span class="text-xs font-medium text-gray-600 dark:text-gray-400">
              {{ link.label }}
            </span>
          </NuxtLink>
        </div>
      </div>

      <!-- Right Section: Avatar -->
      <NuxtLink to="/profile" class="flex items-center space-x-2">
        <div class="user-avatar">
          <UAvatar
            v-if="userStore.getCurrentUser?.email"
            chip-color="primary"
            chip-text=""
            chip-position="top-right"
            size="sm"
            :src="generateAvatar(userStore.getCurrentUser.email)"
            alt="Avatar"
          />
          <div v-else class="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center">
            <span class="text-gray-500">No Avatar</span>
          </div>
        </div>
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUsersStore } from '~/stores/users';
import { useXPBanksStore } from '~/stores/xpBanks';
import { useCoinWalletsStore } from '~/stores/coinWallets';
import { useSDGsStore } from '~/stores/sdgs'; // Import the SDGs store
import { generateAvatar } from '~/utils/avatar';

// Pinia stores
const userStore = useUsersStore();
const banksStore = useXPBanksStore();
const walletsStore = useCoinWalletsStore();
const sdgsStore = useSDGsStore(); // Initialize SDGs store

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
      sdgsStore.fetchSDGs(), // Fetch SDGs data
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

  // Extract and sort top 3 SDGs by XP
  const top3SDGs = Object.entries(sdgXpFields)
    .filter(([key]) => key.startsWith('sdg') && key.endsWith('Xp'))
    .map(([key, xp]) => {
      const normalizedKey = key.replace('Xp', ''); // Remove `Xp` suffix
      const sdgId = parseInt(normalizedKey.replace('sdg', ''), 10); // Extract SDG ID
      const sdg = sdgsStore.sdgs.find((s) => s.id === sdgId); // Find matching SDG from store
      return {
        sdg: normalizedKey,
        xp: xp as number,
        icon: sdg?.icon, // Use the SDG icon from the store
        to: `${sdgId}`
      };
    })
    .sort((a, b) => b.xp - a.xp) // Sort by XP descending
    .slice(0, 3) // Take the top 3
    .map((sdgData) => ({
      // title: `${sdgData.sdg.replace('sdg', '')}`,
      // label: `${sdgData.sdg.replace('sdg', 'SDG ')}: ${sdgData.xp.toFixed(0)}`,
      label: `${sdgData.xp.toFixed(0)} XP`,
      icon: sdgData.icon, // Use the SDG icon from the store
      to: sdgData.to,
    }));

  // Populate links
  links.value = [
    {
      label: 'Worlds',
      to: '/worlds',
    },
    {
      label: `SDG XP: ${totalXp.toFixed(0)}`,
    },
    {
      label: `SDG Coins: ${coins.toFixed(0)}`,
    },
    ...top3SDGs,
  ];
};

onMounted(fetchData);
</script>

