<template>
  <nav class="w-full h-16 bg-white shadow-md flex items-center">
    <div v-if="loading" class="flex justify-center items-center">
      <span class="text-gray-500">Loading...</span>
    </div>

    <div v-else class="w-full flex justify-between items-center px-1 py-1 flex-nowrap overflow-x-auto">
    <div class="flex items-center space-x-6">
        <NuxtLink
          v-for="(link, index) in links.slice(0, 1)"
          :key="index"
          :to="link.to || '#'"
          class="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-primary"
        >
          <component :is="link.icon" class="w-5 h-5" v-if="typeof link.icon === 'string'" />
          <component :is="link.icon" v-else class="w-5 h-5" />
          <span>{{ link.label }}</span>
        </NuxtLink>
    </div>

      <!-- World Display -->
      <div v-if="gameStore.getSDG" class="flex items-center space-x-4">
        <span>World:</span>
        <div class="w-8 h-8 flex items-center justify-center">
          <img
            :src="sdgIconSrc"
            :alt="`SDG ${gameStore.getSDG} Icon`"
            class="w-full h-full object-contain"
          />
        </div>
      </div>

      <!-- Level Display -->
      <div v-if="gameStore.getLevel" class="flex items-center space-x-4">
        <span>Level:</span>
        <div class="flex items-end space-x-1">
          <!-- Render podium steps based on the level -->
          <template v-if="gameStore.getLevel === 1">
            <UIcon name="mdi-signal-cellular-1" class="w-10 h-10" :style="{ color: sdgColor }" />
          </template>
          <template v-else-if="gameStore.getLevel === 2">
            <UIcon name="mdi-signal-cellular-2" class="w-10 h-10" :style="{ color: sdgColor }" />
          </template>
          <template v-else-if="gameStore.getLevel === 3">
            <UIcon name="mdi-signal-cellular-3" class="w-10 h-10" :style="{ color: sdgColor }" />
          </template>
        </div>
        <!--        <span
          class="px-3 py-1 rounded-md border font-semibold"
          :class="getLevelClass(gameStore.getLevel)"
        >
    {{ getRomanLevel(gameStore.getLevel) }}
        </span> -->
      </div>

      <div class="flex items-center space-x-4">
        <span>Stage:</span>
        <span class="font-semibold">
          <template v-if="gameStore.getStage === 'Exploring'">
            <Icon name="mdi-person-search" /> {{ gameStore.getStage }}
          </template>
          <template v-else-if="gameStore.getStage === 'Labeling'">
            <Icon name="mdi-tag-outline" /> {{ gameStore.getStage }}
          </template>
          <template v-else-if="gameStore.getStage === 'Voting'">
            <Icon name="mdi-vote" /> {{ gameStore.getStage }}
          </template>
          <template v-else>
            {{ gameStore.getStage }}
          </template>
        </span>
      </div>

      <!-- Quadrant Display -->
      <div class="flex items-center space-x-4">
        <span>Situation:</span>
        <!-- Render only the active quadrant -->
        <div class="p-1 border rounded-md w-10 h-10 text-xs flex flex-col items-center justify-between">

          <!-- Many Publications, All SDGs -->
          <template v-if="gameStore.getQuadrant === Quadrant.MANY_PUBS_ALL_SDG">
            <div class="flex space-x-0.5">
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
            </div>
            <div class="flex space-x-0.5">
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
            </div>
          </template>

          <!-- Many Publications, 1 SDG -->
          <template v-if="gameStore.getQuadrant === Quadrant.MANY_PUBS_ONE_SDG">
            <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
            <div class="flex space-x-0.5">
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
            </div>
          </template>

          <!-- 1 Publication, All SDGs -->
          <template v-if="gameStore.getQuadrant === Quadrant.ONE_PUB_ALL_SDG">
            <div class="flex space-x-0.5">
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
            </div>
            <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
          </template>

          <!-- 1 Publication, 1 SDG -->
          <template v-if="gameStore.getQuadrant === Quadrant.ONE_PUB_ONE_SDG">
            <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
            <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
          </template>
        </div>
      </div>

      <div
        v-for="(link, index) in links.slice(1, 3)"
        :key="index"
        class="flex items-center space-x-2 text-sm font-medium text-gray-700"
      >
        <span>{{ link.label }}</span>
      </div>

      <div>Your Top SDGs</div>
      <div
        v-for="(link, index) in links.slice(3)"
        :key="index"
        class="flex flex-col items-center space-y-1"
      >
        <NuxtLink :to="{ path: `/exploration/sdgs/${link.to}/1` }">
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
          <span class="text-xs font-medium text-gray-600">
              {{ link.label }}
            </span>
        </NuxtLink>
      </div>

      <!-- Right Section: Avatar -->
      <div class="flex items-center space-x-6">

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <span v-if="currentRank" class="font-semibold text-gray-700 whitespace-nowrap">
            {{ currentRank.name }}
          </span>
        </div>

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <span v-if="currentRank" class="text-sm text-gray-500 whitespace-nowrap">
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

        <NuxtLink :to="{ path: `/users/${userStore.getCurrentUser?.userId}`}"  class="flex items-center space-x-2">
          <div class="user-avatar">
            <UAvatar
              v-if="userStore.getCurrentUser?.email"
              size="sm"
              :src="generateAvatar(userStore.getCurrentUser.email)"
              alt="Avatar"
            />
            <div v-else class="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center">
              <span class="text-gray-500">No Avatar</span>
            </div>
          </div>
        </NuxtLink>

        <div class="drawer drawer-end z-10">
          <input id="drawer-help" type="checkbox" class="drawer-toggle hidden" />
          <div class="drawer-content">
            <UButton size="sm" color="primary" variant="solid" onclick="document.getElementById('drawer-help').checked = true;">
              Help
            </UButton>
          </div>

          <div class="drawer-side">
            <label for="drawer-help" aria-label="close sidebar" class="drawer-overlay"></label>

            <div class="menu bg-base-200 text-base-content min-h-full w-1/5 p-4">

              <div class="flex justify-center h-full">
                <div class="grid grid-flow-col grid-cols-3 grid-rows-3 gap-4 w-80 h-80 border border-gray-300 bg-white p-2 rounded-md">

                  <div class="col-span-1 row-span-1flex flex-col items-center justify-center bg-white text-black font-bold p-2 rounded-md">
                  </div>

                  <!-- Publications Label (Y-axis, Vertical) -->
                  <div class="row-span-2 flex flex-col items-center justify-center text-black font-bold p-2 rounded-md">
                    <span class="transform rotate-180 whitespace-nowrap [writing-mode:vertical-lr]">Publications (N - 1)</span>
                    <Icon name="line-md-document" class="w-5 h-5 text-black mt-1"/>
                  </div>

                  <!-- SDGs Label (X-axis) -->
                  <div class="col-span-2 flex flex-col items-center justify-center text-black font-bold p-2 rounded-md">
                    <span>SDGs (17 - 1)</span>
                    <Icon name="ph-hexagon-light" class="w-5 h-5 text-black mt-1"/>
                  </div>

                  <!-- Quadrant: Many Publications, All SDGs -->
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center border border-gray-300 rounded-md shadow-md"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.MANY_PUBS_ALL_SDG }">
                    <div class="flex space-x-1">
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                    </div>
                    <div class="flex space-x-1 mt-1">
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                    </div>
                  </div>

                  <!-- Quadrant: 1 Publication, All SDGs -->
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center  border border-gray-300 rounded-md shadow-md"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.ONE_PUB_ALL_SDG }">
                    <div class="flex space-x-1">
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                    </div>
                    <Icon name="line-md-document" class="w-5 h-5 text-gray-600 mt-1"/>
                  </div>

                  <!-- Quadrant: Many Publications, 1 SDG -->
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center border border-gray-300 rounded-md shadow-md"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.MANY_PUBS_ONE_SDG }">
                    <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
                    <div class="flex space-x-1 mt-1">
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                    </div>
                  </div>

                  <!-- Quadrant: 1 Publication, 1 SDG -->
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center border border-gray-300 rounded-md shadow-md"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.ONE_PUB_ONE_SDG }">
                    <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
                    <Icon name="line-md-document" class="w-5 h-5 text-gray-600 mt-1"/>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useUsersStore } from "~/stores/users";
import { useXPBanksStore } from "~/stores/xpBanks";
import { useCoinWalletsStore } from "~/stores/coinWallets";
import { useSDGsStore } from "~/stores/sdgs";
import { useGameStore } from "~/stores/game";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { generateAvatar } from "~/utils/avatar";
import { Quadrant } from "~/types/enums";
import {useToast} from "#ui/composables/useToast";


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

const checkUpdates = async () => {
  const toast = useToast();
  try {
    await banksStore.fetchLatestXPBankHistory();
    const latestXP = banksStore.latestXPBankHistory;
    if (latestXP && latestXP.increment) {
      toast.add({
        title: `XP Earned!`,
        description: `You earned ${latestXP.increment} XP! Reason: ${latestXP.reason}`,
        timeout: 5000
      });
    }
  } catch (error) {
    console.error("Failed to fetch latest XP update", error);
  }

  try {
    await walletsStore.fetchLatestSDGCoinWalletHistory();
    const latestWallet = walletsStore.latestSDGCoinWalletHistory;
    if (latestWallet && latestWallet.increment) {
      toast.add({
        title: `Coins Earned!`,
        description: `You earned ${latestWallet.increment} coins! Reason: ${latestWallet.reason}`,
        timeout: 5000
      });
    }
  } catch (error) {
    console.error("Failed to fetch latest wallet update", error);
  }
};

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
    { label: 'Game Mode', to: '/scenarios' },
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

const sdgIconSrc = computed(() => {
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === gameStore.getSDG);
  return `data:image/svg+xml;base64,${sdg.icon}`;
});

onMounted(() => {
  fetchData();
  setInterval(() => {
    checkUpdates();
  }, 10000); // Check every minute
});
</script>
