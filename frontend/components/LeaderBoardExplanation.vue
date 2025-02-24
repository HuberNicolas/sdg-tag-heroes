<template>
  <div class="">
    <!--
    <h2 class="text-2xl font-bold mb-4 text-center text-gray-800">
      Rank Tier Explanation - {{ currentSDG ? `SDG${currentSDG.id} - ${currentSDG.shortTitle}` : "Please select an SDG" }}
    </h2>
    -->

    <div v-if="loading" class="text-blue-500 text-lg text-center">Loading tiers...</div>
    <div v-if="error" class="text-red-500 text-lg text-center">
      <p>An error occurred: {{ error }}</p>
    </div>
    <!--
    <div v-if="!currentSDG && !loading" class="text-center text-gray-600 text-lg">Please select an SDG to view rank tiers.</div>
    -->

    <div v-if="currentSDG && tiers.length > 0" class="overflow-x-auto">
      <table class="w-full border-collapse">
        <thead class="bg-gray-100">
        <tr class="text-left text-gray-700">
          <th class="p-1 border border-gray-300 text-center">Tier</th>
          <th class="p-1 border border-gray-300">Rank Name</th>
          <th class="p-1 border border-gray-300">Description</th>
          <th class="p-1 border border-gray-300 text-center">XP Required</th>
          <th class="p-1 border border-gray-300 text-center">Symbol</th>
        </tr>
        </thead>
        <tbody class="bg-white">
        <tr v-for="tier in tiers" :key="tier.rankId" class="hover:bg-gray-50 transition duration-200">
          <!-- Tier Number -->
          <td class="p-1 border border-gray-300 text-center font-semibold text-gray-700">
            {{ tier.tier }}
          </td>

          <!-- Rank Name -->
          <td class="p-1 border border-gray-300 whitespace-nowrap">
              <span :style="{ backgroundColor: sdgColor }" class="px-3 py-1 rounded-lg text-white text-sm font-semibold">
                {{ tier.name }}
              </span>
          </td>

          <!-- Rank Description -->
          <td class="p-1 border border-gray-300 text-gray-700">
            {{ tier.description || "No description available." }}
          </td>

          <!-- XP Required -->
          <td class="p-1 border border-gray-300 text-center text-lg font-semibold text-gray-800">
            {{ tier.xpRequired }}
          </td>

          <!-- Rank Symbol -->
          <td class="p-1 border border-gray-300 text-center">
            <Icon v-if="tier.tier === 1" name="line-md:chevron-up" :style="{ color: sdgColor }" class="w-6 h-6" />
            <Icon v-else-if="tier.tier === 2" name="line-md:chevron-double-up" :style="{ color: sdgColor }" class="w-6 h-6" />
            <Icon v-else-if="tier.tier === 3" name="line-md:chevron-triple-up" :style="{ color: sdgColor }" class="w-6 h-6" />
            <Icon v-else name="line-md:minus" class="text-gray-400 w-6 h-6" />
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { useSDGsStore } from "~/stores/sdgs";
import { useGameStore} from "~/stores/game";

const rankStore = useSDGRanksStore();
const sdgStore = useSDGsStore();
const gameStore = useGameStore();

const loading = ref(true);
const error = ref<string | null>(null);
const tiers = ref([]);

// Get the selected SDG
const currentSDG = computed(() => {
  const sdgId = gameStore.getSDG;
  return sdgStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Get SDG color dynamically
const sdgColor = computed(() => {
  return currentSDG.value ? sdgStore.getColorBySDG(currentSDG.value.id) : "#A0A0A0";
});

watch(currentSDG, async (newSDG) => {
  if (newSDG) {
    await updateTiers();
  }
});

onMounted(async () => {
  await rankStore.fetchSDGRanks(); // Load all ranks
  if (currentSDG.value) {
    await updateTiers();
    loading.value = false; // Set loading to false after updating tiers
  } else {
    loading.value = false; // Set loading to false if no SDG is selected
  }
});


async function updateTiers() {
  if (!currentSDG.value) {
    tiers.value = [];
    return;
  }
  tiers.value = rankStore.sdgRanks.filter((rank) => rank.sdgGoalId === currentSDG.value.id);
}
</script>
