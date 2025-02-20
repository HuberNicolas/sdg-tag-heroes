<template>
  <div class="mt-6 w-full max-w-4xl rounded-lg bg-white p-4 shadow-md">
    <!-- Explanation Section -->
    <div class="mb-4 text-sm text-gray-600">
      <p>Not sure which Sustainable Development Goal (SDG) aligns with your skills or interests? Enter your input below and get a suggestion!</p>
    </div>

    <!-- Toggle Switch -->
    <div class="mb-4 flex items-center justify-center">
      <div class="flex items-center gap-4">
        <!-- Skills Radio Button -->
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            v-model="selectedOption"
            value="skills"
            @change="updateMode('skills')"
            class="radio"
          />
          <span :class="{'text-gray-500': selectedOption !== 'skills'}">Skills</span>
        </label>

        <!-- Interests Radio Button -->
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            v-model="selectedOption"
            value="interests"
            @change="updateMode('interests')"
            class="radio"
          />
          <span :class="{'text-gray-500': selectedOption !== 'interests'}">Interests</span>
        </label>
      </div>
    </div>

    <!-- Input Section -->
    <div>
      <input
        v-model="userInput"
        type="text"
        class="mb-2 w-full rounded-md border border-gray-300 p-2 text-gray-700 focus:outline-none focus:ring-1 focus:ring-gray-500"
        :placeholder="selectedOption === 'interests' ? 'e.g., environment, education' : 'e.g., programming, problem-solving'"
      />
      <UButton
        @click="handleGenerateSuggestion"
        :color="'primary'"
        :variant="'solid'"
        :disabled="loading"
        :loading="loading"
      >
        <template v-if="loading">
          <div class="flex items-center justify-center">
            Loading...
          </div>
        </template>
        <template v-else>
          Get SDG Suggestion
        </template>
      </UButton>
    </div>

    <!-- SDG Suggestion Output -->
    <div v-if="proposedSdg" class="mt-4 rounded-md p-3 text-gray-800">
      <div v-if="proposedSdg.proposedSdgId" class="mt-4 rounded-md p-3">
        <img
          v-if="sdgIcon"
          :src="`data:image/svg+xml;base64,${sdgIcon}`"
          :alt="`SDG ${proposedSdg.proposedSdgId} Icon`"
          class="w-8 h-8 object-contain mt-2"
        />
      </div>
      <p :style="{ backgroundColor: suggestedSdgColor }" ><strong>SDG:</strong> {{ proposedSdg.proposedSdgId }}</p>
      <p :style="{ backgroundColor: suggestedSdgColor }"><strong>Reasoning:</strong> {{ proposedSdg.reasoning }}</p>
    </div>

  </div>
</template>

<script>
import { useGameStore } from "@/stores/game";
import { useSDGsStore } from "@/stores/sdgs";
import useGPTAssistantService from "@/composables/useGPTAssistantService";

export default {
  data() {
    return {
      selectedOption: 'skills', // Default to 'skills'
      userInput: "",
      loading: false,
    };
  },
  computed: {
    proposedSdg() {
      return this.selectedOption === 'interests' ? useGameStore().proposedSdgFromInterests : useGameStore().proposedSdgFromSkills;
    },
    sdgIcon() {
      const sdgsStore = useSDGsStore();
      const sdgId = this.proposedSdg?.proposedSdgId;
      if (sdgId && sdgsStore.sdgs.length > 0) {
        const sdg = sdgsStore.sdgs.find((goal) => goal.id === sdgId);
        return sdg ? sdg.icon : null;
      }
      return null;
    },
    suggestedSdgColor() {
      const sdgsStore = useSDGsStore();
      const sdgId = this.proposedSdg?.proposedSdgId;
      if (sdgId && sdgsStore.sdgs.length > 0) {
        const sdg = sdgsStore.sdgs.find((goal) => goal.id === sdgId);
        return sdg ? sdg.color : '#F0F0F0'; // Fallback to a light color if no color is found
      }
      return '#F0F0F0'; // Fallback color
    },
  },
  methods: {
    updateMode(option) {
      this.selectedOption = option;
    },

    async handleGenerateSuggestion() {
      this.loading = true;
      const gameStore = useGameStore();
      const { proposeSdgBasedOnSkills, proposeSdgBasedOnInterests } = useGPTAssistantService();
      try {
        if (this.userInput) {
          const response = this.selectedOption === 'interests'
            ? await proposeSdgBasedOnInterests({ interests: this.userInput })
            : await proposeSdgBasedOnSkills({ skills: this.userInput });

          if (this.selectedOption === 'interests') {
            gameStore.setProposedSdgFromInterests(response);
          } else {
            gameStore.setProposedSdgFromSkills(response);
          }
        }
      } catch (error) {
        console.error("Error generating SDG suggestion:", error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
