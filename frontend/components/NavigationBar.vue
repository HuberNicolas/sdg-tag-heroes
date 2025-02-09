<template>
  <nav class="w-full bg-white shadow-md dark:bg-gray-800">
    <div v-if="loading" class="flex justify-center items-center">
      <span class="text-gray-500">Loading...</span>
    </div>

    <div v-else class="max-w-7xl mx-auto flex justify-between items-center px-1 py-1">
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

      <!-- Quadrant Display -->
      <div class="flex flex-col items-center space-y-2">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-200">Situation:</span>

        <div class="grid grid-cols-2 gap-1 border p-1 rounded-md w-20 h-20 text-xs">
          <!-- 1 Publication, 1 SDG -->
          <div class="relative flex flex-col items-center justify-center p-1 border rounded-md hover:bg-blue-100"
               :class="{ 'bg-blue-200': gameStore.getQuadrant === Quadrant.ONE_PUB_ONE_SDG }">
            <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
            <Icon name="ph-hexagon-light" class="w-4 h-4 text-green-500"/>
            <span class="absolute opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-gray-600">1 Pub, 1 SDG</span>
          </div>

          <!-- 1 Publication, All SDGs -->
          <div class="relative flex flex-col items-center justify-center p-1 border rounded-md hover:bg-blue-100"
               :class="{ 'bg-blue-300': gameStore.getQuadrant === Quadrant.ONE_PUB_ALL_SDG }">
            <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
            <div class="flex space-x-0.5">
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-red-500"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-blue-500"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-yellow-500"/>
            </div>
            <span class="absolute opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-gray-600">1 Pub, All SDGs</span>
          </div>

          <!-- Many Publications, 1 SDG -->
          <div class="relative flex flex-col items-center justify-center p-1 border rounded-md hover:bg-blue-100"
               :class="{ 'bg-blue-400': gameStore.getQuadrant === Quadrant.MANY_PUBS_ONE_SDG }">
            <div class="flex space-x-0.5">
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
            </div>
            <Icon name="ph-hexagon-light" class="w-4 h-4 text-green-500"/>
            <span class="absolute opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-gray-600">Many Pubs, 1 SDG</span>
          </div>

          <!-- Many Publications, All SDGs -->
          <div class="relative flex flex-col items-center justify-center p-1 border rounded-md hover:bg-blue-100"
               :class="{ 'bg-blue-500': gameStore.getQuadrant === Quadrant.MANY_PUBS_ALL_SDG }">
            <div class="flex space-x-0.5">
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
            </div>
            <div class="flex space-x-0.5">
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-red-500"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-blue-500"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-yellow-500"/>
            </div>
            <span class="absolute opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-gray-600">Many Pubs, All SDGs</span>
          </div>
        </div>
      </div>


      <!-- Level Display -->
      <div class="flex items-center space-x-4">
        <span>Current Level:</span>
        <span
          class="px-3 py-1 rounded-md border font-semibold"
          :class="getLevelClass(gameStore.getLevel)"
        >
          {{ getRomanLevel(gameStore.getLevel) }}
        </span>
      </div>


      <div class="flex items-center space-x-4">
        <span>Stage:</span>
        <span class="font-semibold text-purple-600 dark:text-purple-400">
          <template v-if="gameStore.getStage === 'Exploring'">
            <Icon name="magnifying-glass" /> {{ gameStore.getStage }}
          </template>
          <template v-else-if="gameStore.getStage === 'Labeling'">
            <Icon name="label" /> {{ gameStore.getStage }}
          </template>
          <template v-else-if="gameStore.getStage === 'Voting'">
            <Icon name="thumbs-up" /> {{ gameStore.getStage }}
          </template>
          <template v-else>
            {{ gameStore.getStage }}
          </template>
        </span>
      </div>

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

      <!-- Right Section: Avatar -->
      <div class="flex items-center space-x-6">

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <span v-if="currentRank" class="font-semibold text-gray-700 dark:text-gray-300">
            {{ currentRank.name }}
          </span>
        </div>

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <span v-if="currentRank" class="text-sm text-gray-500 dark:text-gray-400">
            Tier {{ currentRank.tier }}
          </span>
        </div>

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <!-- Rank Symbol (Chevron Icons) -->
          <Icon
            v-if="currentRank?.tier === 1"
            name="line-md:chevron-up"
            :style="{ color: sdgColor }"
            class="w-6 h-6"
          />
          <Icon
            v-else-if="currentRank?.tier === 2"
            name="line-md:chevron-double-up"
            :style="{ color: sdgColor }"
            class="w-6 h-6"
          />
          <Icon
            v-else-if="currentRank?.tier === 3"
            name="line-md:chevron-triple-up"
            :style="{ color: sdgColor }"
            class="w-6 h-6"
          />
          <Icon v-else name="line-md:minus" class="text-gray-400 w-6 h-6" />
        </div>

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

        <div class="drawer drawer-end">
          <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
          <div class="drawer-content">
            <!-- Page content here -->
            <label for="my-drawer-4" class="drawer-button btn btn-primary">Help</label>
          </div>
          <div class="drawer-side">
            <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
            <ul class="menu bg-base-200 text-base-content min-h-full w-80 p-4">
              <!-- Sidebar content here -->
              <li><a>Sidebar Item 1</a></li>
              <li><a>Sidebar Item 2</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUsersStore } from '~/stores/users';
import { useXPBanksStore } from '~/stores/xpBanks';
import { useCoinWalletsStore } from '~/stores/coinWallets';
import { useSDGsStore } from '~/stores/sdgs';
import { useGameStore } from '~/stores/game';
import { useSDGRanksStore } from '~/stores/sdgRanks';
import { generateAvatar } from '~/utils/avatar';
import { Quadrant } from "~/types/enums";


// Pinia stores
const userStore = useUsersStore();
const banksStore = useXPBanksStore();
const walletsStore = useCoinWalletsStore();
const sdgsStore = useSDGsStore();
const gameStore = useGameStore();
const rankStore = useSDGRanksStore();

// State
const loading = ref(true);
const links = ref<Array<any>>([]);

const fetchData = async () => {
  try {
    // First fetch the user data
    await userStore.fetchPersonalUser();

    // Then fetch all other data in parallel
    await Promise.all([
      walletsStore.fetchPersonalSDGCoinWallet(),
      banksStore.fetchPersonalXPBank(),
      sdgsStore.fetchSDGs(),
      rankStore.fetchSDGRankByUserId(userStore.getCurrentUser?.userId || 0),
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

  const top3SDGs = Object.entries(sdgXpFields)
    .filter(([key]) => key.startsWith('sdg') && key.endsWith('Xp'))
    .map(([key, xp]) => {
      const normalizedKey = key.replace('Xp', '');
      const sdgId = parseInt(normalizedKey.replace('sdg', ''), 10);
      const sdg = sdgsStore.sdgs.find((s) => s.id === sdgId);
      return {
        sdg: normalizedKey,
        xp: xp as number,
        icon: sdg?.icon,
        to: `${sdgId}`,
      };
    })
    .sort((a, b) => b.xp - a.xp)
    .slice(0, 3)
    .map((sdgData) => ({
      label: `${sdgData.xp.toFixed(0)} XP`,
      icon: sdgData.icon,
      to: sdgData.to,
    }));

  links.value = [
    { label: 'Worlds', to: '/worlds' },
    { label: `Total SDG XP: ${totalXp.toFixed(0)}` },
    { label: `SDG Coins: ${coins.toFixed(0)}` },
    ...top3SDGs,
  ];
};

const currentRank = computed(() => {
  if (!gameStore.getSDG || !rankStore.userSDGRank) return null;

  return rankStore.userSDGRank.find(
    rank => rank.sdgGoalId === gameStore.getSDG
  ) || rankStore.userSDGRank[0];
});

// Get the currently selected SDG
const currentSDG = computed(() => {
  const sdgId = gameStore.getSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Computed property to get the color of the selected SDG
const sdgColor = computed(() => {
  return currentSDG.value ? sdgsStore.getColorBySDG(currentSDG.value.id) : "#A0A0A0"; // Default gray if no SDG
});

// Convert level to Roman numerals
const getRomanLevel = (level: number | null) => {
  if (level === null) return "N/A";
  const romanNumerals = ["I", "II", "III"];
  return level > 0 && level <= 10 ? romanNumerals[level - 1] : level;
};

// Assign tier color based on level
const getLevelClass = (level: number | null) => {

  if (level === 1) return "bg-orange-200 border-orange-400 text-orange-800"; // Bronze
  if (level === 2) return "bg-gray-200 border-gray-400 text-gray-700"; // Silver
  if (level === 3) return "bg-yellow-200 border-yellow-500 text-yellow-800"; // Gold
  else return "bg-gray-200 border-gray-400 text-gray-700";
};

onMounted(fetchData);
</script>
