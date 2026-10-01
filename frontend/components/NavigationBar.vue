<template>
  <nav class="relative z-20 w-full min-h-[var(--nav-h)] flex items-center border-b border-line bg-surface/70 backdrop-blur-xl">
    <div v-if="loading" class="flex justify-center items-center gap-3 w-full h-[var(--nav-h)] font-mono text-sm text-fg-dim">
      <Icon
        :name="loadingHexagon"
        class="w-7 h-7 text-accent transition-all"
      />
      <span>loading<span class="animate-blink">_</span></span>
    </div>

    <div v-else class="w-full max-w-[2560px] mx-auto flex flex-wrap justify-between items-center gap-x-4 gap-y-2 px-4 py-2 text-sm">
      <UModal v-model="isXPModalOpen">
        <div class="p-8 bg-surface rounded-xl shadow-panel flex flex-col items-center text-center space-y-6 max-w-2xl w-full animate-fade-in scale-105 relative">

          <!-- Large Community / Awareness Icon -->
          <div class="relative flex items-center justify-center">
            <Icon
              name="line-md:group"
              class="w-[160px] h-[160px] text-fg-dim opacity-10 absolute"
            />

            <!-- SDG Icon (Smaller) -->
            <div v-if="xpModalContent?.sdg" class="w-20 h-20 bg-muted rounded-lg flex items-center justify-center border-4 z-10" :style="{ borderColor: sdgModalColor }">
              <img
                :src="getSdgIconSrc(xpModalContent.sdg)"
                :alt="`SDG ${xpModalContent.sdg} Icon`"
                class="w-full h-full object-contain rounded-md"
              >
            </div>
          </div>

          <!-- Title -->
          <h2 v-if="xpModalContent?.title" class="text-3xl font-bold text-fg relative z-10">
            {{ xpModalContent.title }}
          </h2>

          <!-- Contribution Message -->
          <h3 class="text-2xl font-semibold text-fg relative z-10">
            Thank you for your label
          </h3>

          <!-- XP Earned Description -->
          <p v-if="xpModalContent?.description" class="text-lg text-fg leading-relaxed relative z-10">
            {{ xpModalContent.description }}
          </p>

          <!-- Additional Awareness / Community Message -->
          <p class="text-md text-fg-dim italic relative z-10">
            Each label is a data point. Together, the community's labels show where the model is right and where it is not.
          </p>

          <!-- Player Rank Section -->
          <div v-if="playerRankData" class="flex flex-col items-center mt-4 relative z-10">
            <p class="text-lg font-semibold text-fg">
              Your Rank in SDG {{ xpModalContent?.sdg.replace('sdg', '') }}
            </p>

            <div class="flex items-center space-x-3 p-3 bg-muted rounded-lg shadow-panel">
              <Icon v-if="playerRankData.tier === 1" name="line-md:chevron-up" class="w-6 h-6" :style="{ color: sdgModalColor }" />
              <Icon v-else-if="playerRankData.tier === 2" name="line-md:chevron-double-up" class="w-6 h-6" :style="{ color: sdgModalColor }" />
              <Icon v-else-if="playerRankData.tier === 3" name="line-md:chevron-triple-up" class="w-6 h-6" :style="{ color: sdgModalColor }" />
              <Icon v-else name="line-md:minus" class="w-6 h-6 text-fg-faint" />

              <span class="px-3 py-1 rounded-lg text-white text-sm font-semibold" :style="{ backgroundColor: sdgModalColor }">
          {{ playerRankData.name }}
        </span>

              <span class="text-lg font-semibold text-fg">
          Tier {{ playerRankData.tier }}
        </span>
            </div>
          </div>

          <!-- XP Earned Display -->
          <div v-if="xpModalContent?.increment" class="flex flex-col items-center mt-4 relative z-10">
            <p class="text-lg font-semibold text-fg">Experience Points Earned</p>
            <span class="text-2xl font-bold" :style="{ color: sdgModalColor }">
        {{ Math.round(xpModalContent.increment) }} XP
      </span>
          </div>

          <!-- Progress Bar Chart -->
          <ProgressBarChart
            v-if="xpModalContent?.sdg && playerRankData"
            :current-xp="Math.round(xpModalContent.xp)"
            :next-level-xp="getNextLevelXp(xpModalContent.sdg, playerRankData.tier)"
            :sdg-color="sdgModalColor"
            class="relative z-10"
          />

          <!-- Closing Note -->
          <p class="text-sm text-fg-dim italic relative z-10">
            XP count your experience per SDG; they raise your rank and open new universes.
          </p>

          <!-- Close Button -->
          <UButton
            label="Continue"
            class="px-8 py-3 text-white text-lg font-semibold rounded-lg hover:bg-opacity-80 transition-all relative z-10"
            :style="{ backgroundColor: sdgModalColor }"
            @click="closeXPModal"
          />
        </div>
      </UModal>


      <UModal v-model="isCoinModalOpen">
        <div class="p-8 bg-surface rounded-xl shadow-panel flex flex-col items-center text-center space-y-6 max-w-2xl w-full animate-fade-in scale-105 relative">

          <!-- Title -->
          <h2 v-if="coinModalContent?.title" class="text-3xl font-bold text-fg relative z-10 mb-4">
            {{ coinModalContent.title }}
          </h2>

          <!-- Large Publication Icon (Now wrapping SDG Icon) -->
          <div class="relative flex items-center justify-center p-4">
            <Icon
              name="line-md:document"
              class="w-[200px] h-[200px] text-fg-dim opacity-10 absolute"
            />

            <!-- SDG Icon (Smaller) -->
            <div v-if="coinModalContent?.sdg" class="w-20 h-20 bg-muted rounded-lg flex items-center justify-center border-4 z-10">
              <img
                :src="getSdgIconSrc(coinModalContent.sdg)"
                :alt="`SDG ${coinModalContent.sdg} Icon`"
                class="w-full h-full object-contain rounded-md"
              >
            </div>
          </div>



          <!-- Contribution Message -->
          <h3 v-if="coinModalContent?.title" class="text-2xl font-semibold text-fg relative z-10">
            Coins for your contribution
          </h3>

          <!-- Coin Earned Description -->
          <p v-if="coinModalContent?.description" class="text-lg text-fg leading-relaxed relative z-10">
            {{ coinModalContent.description }}
          </p>

          <!-- Additional Value Proposition -->
          <p class="text-md text-fg-dim italic relative z-10">
            Coins are the second currency of the game, collected per SDG.
          </p>

          <!-- Coins Earned Display -->
          <div v-if="coinModalContent?.increment" class="flex flex-col items-center mt-4 relative z-10">
            <p class="text-lg font-semibold">Coins Earned</p>
            <span class="text-2xl font-bold" :style="{ color: sdgModalColor }">
        {{ Math.round(coinModalContent.increment) }} Coins
      </span>
          </div>

          <!-- Closing Note -->
          <p class="text-sm text-fg-dim italic relative z-10">
            Your balance is shown in the navigation bar.
          </p>

          <!-- Close Button -->
          <UButton
            label="Continue"
            class="px-8 py-3 text-white text-lg font-semibold rounded-lg hover:bg-opacity-80 transition-all relative z-10"
            :style="{ backgroundColor: sdgModalColor }"
            @click="closeCoinModal"
          />
        </div>
      </UModal>



      <!-- Brand: leads back to the game modes -->
      <NuxtLink
        v-for="(link, index) in links.slice(0, 1)"
        :key="index"
        :to="link.to || '#'"
        class="group flex items-center gap-2.5"
        :title="link.label"
      >
        <span class="nav-logo" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none">
            <path d="M16 3.5 26.8 9.75v12.5L16 28.5 5.2 22.25V9.75Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
            <path d="M16 10.5 20.8 13.25v5.5L16 21.5l-4.8-2.75v-5.5Z" fill="currentColor" />
          </svg>
        </span>
        <span class="flex flex-col leading-none">
          <span class="font-pixel text-[10px] text-fg">SDG Tag Heroes</span>
          <span class="mt-1.5 hidden xl:block font-mono text-[11px] text-fg-dim transition-colors group-hover:text-accent">
            ← {{ link.label.toLowerCase() }}
          </span>
        </span>
      </NuxtLink>

      <!-- Where the player is: world, level and stage -->
      <div class="flex items-center gap-1 rounded-full border border-line bg-surface/70 p-1 font-mono text-xs">
        <div v-if="gameStore.getSDG" class="nav-ctx" title="SDG world">
          <span class="nav-ctx__key">world</span>
          <img
            :src="sdgIconSrc"
            :alt="`SDG ${gameStore.getSDG} Icon`"
            class="w-6 h-6 rounded-md object-contain"
          >
        </div>

        <div v-if="gameStore.getLevel" class="nav-ctx" title="Level">
          <span class="nav-ctx__key">level</span>
          <template v-if="gameStore.getLevel === 1">
            <UIcon name="mdi-signal-cellular-1" class="w-5 h-5" :style="{ color: sdgColor }" />
          </template>
          <template v-else-if="gameStore.getLevel === 2">
            <UIcon name="mdi-signal-cellular-2" class="w-5 h-5" :style="{ color: sdgColor }" />
          </template>
          <template v-else-if="gameStore.getLevel === 3">
            <UIcon name="mdi-signal-cellular-3" class="w-5 h-5" :style="{ color: sdgColor }" />
          </template>
        </div>

        <div class="nav-ctx" title="Stage">
          <span class="nav-ctx__key">stage</span>
          <span class="flex items-center gap-1 font-medium text-fg">
            <template v-if="gameStore.getStage === 'Exploring'">
              <Icon name="mdi-person-search" class="text-accent" /> {{ gameStore.getStage }}
            </template>
            <template v-else-if="gameStore.getStage === 'Labeling'">
              <Icon name="mdi-tag-outline" class="text-accent" /> {{ gameStore.getStage }}
            </template>
            <template v-else-if="gameStore.getStage === 'Voting'">
              <Icon name="mdi-vote" class="text-accent" /> {{ gameStore.getStage }}
            </template>
            <template v-else>
              {{ gameStore.getStage || '—' }}
            </template>
          </span>
        </div>
      </div>

      <!-- Wallet: XP and coins -->
      <div class="flex items-center gap-2">
        <span
          v-for="(link, index) in links.slice(1, 3)"
          :key="index"
          class="stat-pill"
        >
          <Icon :name="index === 0 ? 'mdi-star-four-points-outline' : 'mdi-hexagon-multiple-outline'" class="w-3.5 h-3.5 text-accent" />
          <span class="hidden 2xl:inline">{{ link.label.split(': ')[0] }}</span>
          <span class="2xl:hidden">{{ index === 0 ? 'xp' : 'coins' }}</span>
          <b>{{ link.label.split(': ')[1] }}</b>
        </span>
      </div>

      <!-- Top SDGs by XP -->
      <div class="flex items-center gap-2">
        <span class="hidden xl:inline font-mono text-[11px] text-fg-faint">top_sdgs</span>
        <NuxtLink
          v-for="(link, index) in links.slice(3)"
          :key="index"
          :to="{ path: `/exploration/sdgs/${link.to}/1` }"
          class="group flex items-center gap-1.5 rounded-lg border border-line bg-surface/70 py-0.5 pl-0.5 pr-2 transition-all hover:-translate-y-0.5 hover:border-line-strong"
          :title="`SDG ${link.to}`"
        >
          <img
            v-if="link.icon"
            :src="`data:image/svg+xml;base64,${link.icon}`"
            :alt="`SDG ${index + 1} Icon`"
            class="w-6 h-6 rounded-md object-contain"
          >
          <span class="font-mono text-[11px] text-fg-dim group-hover:text-fg">{{ link.label }}</span>
        </NuxtLink>
      </div>

      <!-- Right: rank, avatar, about, theme and help -->
      <div class="flex items-center gap-2">
        <div
          v-if="gameStore.getSDG && currentRank"
          class="flex items-center gap-1.5 rounded-full border border-line bg-surface/70 py-1 pl-2 pr-3"
          :title="`Your rank in this SDG world: ${currentRank.name}`"
        >
          <!-- Rank Symbol (Chevron Icons) -->
          <Icon
            v-if="currentRank?.tier === 1"
            name="line-md:chevron-up"
            :style="{ color: sdgColor }"
            class="w-5 h-5"
          />
          <Icon
            v-else-if="currentRank?.tier === 2"
            name="line-md:chevron-double-up"
            :style="{ color: sdgColor }"
            class="w-5 h-5"
          />
          <Icon
            v-else-if="currentRank?.tier === 3"
            name="line-md:chevron-triple-up"
            :style="{ color: sdgColor }"
            class="w-5 h-5"
          />
          <Icon v-else name="line-md:minus" class="text-fg-faint w-5 h-5" />
          <span class="hidden 2xl:inline font-semibold text-fg whitespace-nowrap">{{ currentRank.name }}</span>
          <span class="font-mono text-[11px] text-fg-dim whitespace-nowrap">tier {{ currentRank.tier }}</span>
        </div>

        <NuxtLink
          :to="{ path: `/users/${userStore.getCurrentUser?.userId}`}"
          class="grid h-8 w-8 place-items-center overflow-hidden rounded-full ring-1 ring-line transition hover:ring-2 hover:ring-accent"
          title="Your profile"
        >
          <UAvatar
            v-if="userStore.getCurrentUser?.email"
            size="sm"
            :src="generateAvatar(userStore.getCurrentUser.email)"
            alt="Avatar"
          />
          <div v-else class="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
            <Icon name="mdi-account" class="text-fg-dim" />
          </div>
        </NuxtLink>

        <NuxtLink to="/about" class="nav-icon-btn" title="About">
          <Icon name="mdi-information-outline" class="w-[18px] h-[18px]" />
        </NuxtLink>

        <button
          type="button"
          class="nav-icon-btn"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleColorMode"
        >
          <Icon :name="isDark ? 'line-md:sunny-outline' : 'line-md:moon'" class="w-[18px] h-[18px]" />
        </button>

        <div class="drawer drawer-end z-30 !w-auto">
          <input id="drawer-help" type="checkbox" class="drawer-toggle hidden" >
          <div class="drawer-content">
            <UButton size="sm" color="primary" variant="solid" icon="i-mdi-help-hexagon-outline" onclick="document.getElementById('drawer-help').checked = true;">
              Help
            </UButton>
          </div>

          <div class="drawer-side">
            <label for="drawer-help" aria-label="close sidebar" class="drawer-overlay"/>

            <div class="menu bg-base-200 text-base-content min-h-full w-[min(32rem,90vw)] p-4 flex flex-col items-center">
              <UDivider label="SDG Cheatsheet" size="xl" />
              <SDGSelectorHelp/>
              <UDivider label="How to Label" size="xl" />
              <div class="flex flex-col gap-1.5 p-3 border rounded-lg bg-surface-2 text-sm w-full">
                <h3 class="font-semibold text-fg flex items-center gap-1.5">
                  <Icon name="mdi-scale-balance" class="w-4 h-4 text-fg-dim" /> How to Decide
                </h3>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-book-open-variant" class="w-4 h-4 text-fg-dim" />
                  <span>Check title & abstract</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-earth" class="w-4 h-4 text-fg-dim" />
                  <span>Does the research contribute to people or the planet?</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-lightbulb-on-outline" class="w-4 h-4 text-fg-dim" />
                  <span>The model suggests SDGs (see its highlights)</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-account-group" class="w-4 h-4 text-fg-dim" />
                  <span>See community labels</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-check-circle-outline" class="w-4 h-4 text-fg-dim" />
                  <span><b>Yes</b> → Clear SDG link</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-close-circle-outline" class="w-4 h-4 text-fg-dim" />
                  <span><b>No</b> → Unclear or unrelated</span>
                </div>
              </div>
              <!-- <h1 class="text-lg font-bold mb-4 text-center w-full">Situations</h1> -->
              <UDivider label="Situations" size="xl" />
              <div class="flex flex-col gap-4 p-4 bg-surface-2 border rounded-md text-sm">

                <!-- Context Overview -->
                <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                  <Icon name="mdi-map-search-outline" class="w-6 h-6 text-fg mb-2" />
                  <h3 class="font-semibold text-fg">How It Works</h3>
                  <p class="text-fg-dim">
                    Start in an exploration space with many publications and SDGs.
                    Your goal is to <b>drill down step-by-step</b> until you reach a single publication that can be labeled.
                    There are <b>multiple paths</b> possible.
                  </p>
                </div>

                <!-- Decide the Game Mode -->
                <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                  <Icon name="mdi-map-search-outline" class="w-6 h-6 text-fg mb-2" />
                  <h3 class="font-semibold text-fg">Different Game Modes</h3>
                  <p class="text-fg-dim">
                    You can decide between two game modes: Game Mode <b>SDG Specialization</b> and Game Mode <b>Open World Exploration</b>
                  </p>
                </div>

                <!-- Two Main Paths: SDG Specialization vs. Open World -->
                <div class="grid grid-cols-2 gap-4">

                  <!-- Scenario 1: SDG Specialization -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                    <Icon name="mdi-target" class="w-6 h-6 text-fg mb-2" />
                    <h3 class="font-semibold text-fg"><b>SDG Specialization</b></h3>
                    <p class="text-fg-dim">Choose <b>one specific SDG</b> and focus only on publications relevant to that goal.</p>
                  </div>

                  <!-- Scenario 2: Open World Exploration -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                    <Icon name="mdi-earth" class="w-6 h-6 text-fg mb-2" />
                    <h3 class="font-semibold text-fg"><b>Open World Exploration</b></h3>
                    <p class="text-fg-dim">Browse freely across <b>all SDGs</b>, discovering broader research connections.</p>
                  </div>

                  <!-- Many Publications, One SDG -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                    <Icon name="mdi-format-list-bulleted" class="w-6 h-6 text-fg mb-2" />
                    <h3 class="font-semibold text-fg">Focused Search</h3>
                    <p class="text-fg-dim">Drill down into a single SDG, filtering out publications that are unrelated.</p>
                  </div>

                  <!-- Many Publications, All SDGs -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                    <Icon name="mdi-layers-outline" class="w-6 h-6 text-fg mb-2" />
                    <h3 class="font-semibold text-fg">Broad Overview</h3>
                    <p class="text-fg-dim">Analyze a wide set of publications across all SDGs to identify patterns and trends.</p>
                  </div>

                  <!-- One Publication, One SDG -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                    <Icon name="mdi-check-circle-outline" class="w-6 h-6 text-fg mb-2" />
                    <h3 class="font-semibold text-fg">Final Labeling</h3>
                    <p class="text-fg-dim">You’ve reached a single publication. Now it’s time to make the final SDG decision.</p>
                  </div>


                  <!-- One Publication, All SDGs -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-surface shadow-panel">
                    <Icon name="mdi-bookshelf" class="w-6 h-6 text-fg mb-2" />
                    <h3 class="font-semibold text-fg">Several SDGs</h3>
                    <p class="text-fg-dim">Examine a single publication and determine if it contributes to any of the SDGs.</p>
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
import { onMounted, ref, watchEffect } from "vue";
import { useUsersStore } from "~/stores/users";
import { useXPBanksStore } from "~/stores/xpBanks";
import { useCoinWalletsStore } from "~/stores/coinWallets";
import { useSDGsStore } from "~/stores/sdgs";
import { useGameStore } from "~/stores/game";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { generateAvatar } from "~/utils/avatar";
import { usePublicationsStore } from "~/stores/publications";

const publicationsStore = usePublicationsStore();

// Light / dark theme switch
const colorMode = useColorMode();
const isDark = computed(() => colorMode.value === "dark");
const toggleColorMode = () => {
  colorMode.preference = isDark.value ? "light" : "dark";
};

const getPublicationTitle = async (publicationId: number): Promise<string> => {
  try {
    const publication = await publicationsStore.fetchPublicationWithoutStoreById(publicationId);
    return publication?.title || "Unknown Publication";
  } catch (error) {
    console.error(`Failed to fetch publication title: ${error}`);
    return "Unknown Publication";
  }
};

// Pinia stores
const userStore = useUsersStore();
const banksStore = useXPBanksStore();
const walletsStore = useCoinWalletsStore();
const sdgsStore = useSDGsStore();
const gameStore = useGameStore();
const rankStore = useSDGRanksStore();

// State
const loading = ref(true);
interface NavigationLink {
  label: string;
  to?: string;
  icon?: string | null;
}
const links = ref<NavigationLink[]>([]);


//const isOpen = ref(false);
//const modalContent = ref<{ title: string; description: string; xp?: number; increment?: number; sdg?: SDGType; publicationTitle?: string } | null>(null);

const isXPModalOpen = ref(false);
const isCoinModalOpen = ref(false);

const xpModalContent = ref<{ title: string; description: string; xp?: number; increment?: number; sdg?: SDGType; publicationTitle?: string } | null>(null);
const coinModalContent = ref<{ title: string; description: string; increment?: number; sdg?: SDGType; publicationTitle?: string } | null>(null);

const playerRankData = ref<{ name: string; tier: number } | null>(null);

const openXPModal = ({ title, description, sdg, publicationTitle, increment, xp = 0 }) => {
  xpModalContent.value = {
    title,
    description,
    sdg,
    publicationTitle,
    increment,
    xp,
  };

  isXPModalOpen.value = true;
};

const openCoinModal = ({ title, description, sdg, publicationTitle, increment }) => {
  coinModalContent.value = {
    title,
    description,
    sdg,
    publicationTitle,
    increment,
  };

  // Open Coin modal only after XP modal closes
  if (isXPModalOpen.value) {
    setTimeout(() => {
      isCoinModalOpen.value = true;
    }, 3000);
  } else {
    isCoinModalOpen.value = true;
  }
};

const closeXPModal = () => {
  isXPModalOpen.value = false;
  xpModalContent.value = null;

  // Ensure XP modal is fully closed before opening Coin modal
  setTimeout(() => {
    if (!isXPModalOpen.value && coinModalContent.value) {
      isCoinModalOpen.value = true;
    }
  }, 3000); // Small delay to allow modal transition
};

const closeCoinModal = () => {
  isCoinModalOpen.value = false;
  coinModalContent.value = null;
};


const checkUpdates = async () => {
  try {
    await banksStore.fetchLatestXPBankHistory();
    await banksStore.fetchPersonalXPBank();
    const latestXP = banksStore.latestXPBankHistory;

    if (latestXP && latestXP.increment) {
      const publicationId = extractPublicationId(latestXP.reason || "");
      const publicationTitle = publicationId ? await getPublicationTitle(publicationId) : "Unknown Publication";
      const playerRank = getPlayerRank(userStore.getCurrentUser?.userId, latestXP.sdg);
      playerRankData.value = playerRank; // Ensure this is properly set

      const xpForSdg = banksStore.userXPBank ? banksStore.userXPBank[`${latestXP.sdg}Xp`] : 0;

      openXPModal({
        title: `XP earned`,
        description: `You earned ${latestXP.increment} XP for labeling the publication: "${publicationTitle}".`,
        publicationTitle,
        sdg: latestXP.sdg,
        playerRank,
        increment: latestXP.increment,
        xp: xpForSdg,
      });


    }
  } catch (error) {
    console.error("Failed to fetch latest XP update", error);
  }

  try {
    await walletsStore.fetchLatestSDGCoinWalletHistory();
    await banksStore.getUserXPBank;
    const latestWallet = walletsStore.latestSDGCoinWalletHistory;

    if (latestWallet && latestWallet.increment) {
      const publicationId = extractPublicationId(latestWallet.reason || "");
      const publicationTitle = publicationId ? await getPublicationTitle(publicationId) : "Unknown Publication";

      const sdg = extractSDGFromReason(latestWallet.reason || "");
      const playerRank = getPlayerRank(userStore.getCurrentUser?.userId, sdg);
      const coinsForSdg = walletsStore.userSDGCoinWallet ? walletsStore.userSDGCoinWallet[`${sdg}Coins`] : 0;
      // Open the coins-earned modal after the XP modal if both exist
      setTimeout(() => {
        openCoinModal({
          title: `Coins earned`,
          description: `You earned ${latestWallet.increment} SDG Coins for the publication: "${publicationTitle}".`,
          publicationTitle,
          sdg,
          playerRank,
          increment: latestWallet.increment,
          coins: coinsForSdg,
        });
      }, isXPModalOpen.value ? 3000 : 0); // Delay if XP modal is still open
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
      rankStore.fetchSDGRanks()
    ]);

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
const updateLinks = (coins: number, xpData: { totalXp: number; [key: string]: unknown }) => {
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
    { label: 'Change Game Mode', to: '/scenarios' },
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



const sdgIconSrc = computed(() => {
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === gameStore.getSDG);
  return `data:image/svg+xml;base64,${sdg.icon}`;
});

const getSdgIconSrc = (sdgType: SDGType) => {
  // Extract the numeric ID from the SDGType string (e.g., "sdg1" -> 1, "sdg13" -> 13)
  const sdgId = parseInt(sdgType.replace('sdg', ''), 10);

  // Find the SDG object in the store using the numeric ID
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === sdgId);

  // Return the base64-encoded SVG icon if found
  return sdg ? `data:image/svg+xml;base64,${sdg.icon}` : null;
};

const extractPublicationId = (reason: string): number | null => {
  const match = reason.match(/Publication (\d+)/);
  return match ? parseInt(match[1], 10) : null;
};

const getPlayerRank = (userId: number, sdgType: SDGType | null) => {
  // Coin histories without an SDG in their reason (e.g. simulated ones) have no rank
  if (!sdgType) return { name: "No Rank", tier: 0 };
  const sdgId = parseInt(sdgType.replace("sdg", ""), 10);
  const userRankData = rankStore.userSDGRanks.find((u) => u.userId === userId);
  const rank = userRankData?.ranks.find((r) => r.sdgGoalId === sdgId);

  return rank ? { name: rank.name, tier: rank.tier } : { name: "No Rank", tier: 0 };
};

const sdgModalColor = computed(() => {
  if (!xpModalContent.value?.sdg) return "#A0A0A0"; // Default gray if no SDG selected

  const sdgId = parseInt(xpModalContent.value.sdg.replace("sdg", ""), 10);
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === sdgId);

  return sdg ? sdgsStore.getColorBySDG(sdg.id) : "#A0A0A0"; // Use fallback gray if SDG not found
});

// Function to get the XP required for the next level
const getNextLevelXp = (sdgType: string, currentTier: number) => {
  const sdgKey = `sdg_${sdgType.replace('sdg', '')}`;
  const nextTier = currentTier + 1;
  const nextTierKey = `tier_${nextTier}`;

  const sdgData = rankStore.sdgLevels[sdgKey];
  if (sdgData && sdgData[nextTierKey]) {
    return sdgData[nextTierKey].xp_required;
  }
  return 0; // If max level, return 0 or handle accordingly
};

const extractSDGFromReason = (reason: string): string | null => {
  const match = reason.match(/SDG (\d+)/);
  return match ? `sdg${match[1]}` : null;
};


watchEffect(() => {
  if (!loading.value) {
    const userWallet = walletsStore.getUserSDGCoinWallet;
    const userBank = banksStore.getUserXPBank;
    updateLinks(userWallet?.totalCoins || 0, userBank || { totalXp: 0 });
  }
});

const hexagonStages = [
  "mdi:hexagon-slice-1",
  "mdi:hexagon-slice-2",
  "mdi:hexagon-slice-3",
  "mdi:hexagon-slice-4",
  "mdi:hexagon-slice-5",
  "mdi:hexagon-slice-6",
];

const loadingHexagon = ref("mdi:hexagon-slice-1");

onMounted(() => {

  let index = 0;
  setInterval(() => {
    loadingHexagon.value = hexagonStages[index];
    index = (index + 1) % hexagonStages.length;
  }, 500); // Change every 500ms

  fetchData();
  setInterval(() => {
    checkUpdates();
  }, 10000); // Check every minute
});
</script>

<style scoped>
.nav-logo {
  @apply grid h-9 w-9 place-items-center rounded-[10px] border border-line bg-surface text-accent transition-all duration-200;
}
.group:hover .nav-logo {
  @apply -translate-y-0.5 shadow-glow;
}
.nav-logo svg {
  @apply h-6 w-6;
}

.nav-ctx {
  @apply flex items-center gap-1.5 rounded-full px-2.5 py-1;
}
.nav-ctx + .nav-ctx {
  @apply border-l border-line;
}
.nav-ctx__key {
  @apply text-[11px] text-fg-faint;
}

.nav-icon-btn {
  @apply grid h-8 w-8 place-items-center rounded-full border border-line bg-surface/70 text-fg-dim transition-colors hover:border-line-strong hover:text-fg;
}
</style>
