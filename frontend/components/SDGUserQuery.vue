<template>
  <div class="mt-6 w-full max-w-4xl h-full rounded-lg bg-white p-4 shadow-md">
    <!-- Explanation Section -->
    <div class="mb-2 text-sm text-gray-600">
      <p>Not sure which Sustainable Development Goal (SDG) aligns with your skills or interests? Enter your input below and get a suggestion! <span class="text-gray-500">(Your personalized SDG will be recommended by our intelligent agent, making it an exciting and relevant match!)</span></p>
    </div>

    <!-- Input Section -->
    <div>
      <input
        v-model="userInput"
        type="text"
        class="mb-2 w-full rounded-md border border-gray-300 p-2 text-gray-700 focus:outline-none focus:ring-1 focus:ring-gray-500"
        :placeholder="selectedOption === 'interests' ? 'e.g., environment, education' : 'e.g., programming, problem-solving'"
      />
    </div>

    <!-- Toggle Switch -->
    <div class="mb-2 flex items-center justify-between">
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
      <div class="flex justify-center">
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
            Reveal Your SDG
          </template>
        </UButton>
      </div>
    </div>

    <!-- SDG Suggestion Output -->
    <div v-if="proposedSdg" class="rounded-md p-1 text-gray-800">
      <div v-if="proposedSdg.proposedSdgId" class="rounded-md p-1 flex items-start space-x-4">
        <div class="flex flex-col items-center">
          <p :style="{ backgroundColor: suggestedSdgColor }" class="whitespace-nowrap">
            <strong>SDG: {{ proposedSdg.proposedSdgId }}</strong>
          </p>
          <img
            v-if="sdgIcon"
            :src="`data:image/svg+xml;base64,${sdgIcon}`"
            :alt="`SDG ${proposedSdg.proposedSdgId} Icon`"
            class="w-12 h-12 object-contain mt-2"
          />
        </div>
        <div>
          <p :style="{ backgroundColor: suggestedSdgColor }">
            <strong>Reasoning:</strong> {{ proposedSdg.reasoning }}
          </p>
        </div>
      </div>
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
        if (sdg) {
          // Assuming the `sdg.color` is a hex color, e.g., "#FF5733"
          return this.hexToRgba(sdg.color, 0.3); // Adjust the opacity (alpha) value here
        }
      }
      return this.hexToRgba('#F0F0F0', 0.3); // Fallback color with opacity
    },
  },
  methods: {
    updateMode(option) {
      this.selectedOption = option;
    },

    hexToRgba(hex, alpha = 1) {
      let r = 0, g = 0, b = 0;

      // 3 digits hex
      if (hex.length === 4) {
        r = parseInt(hex[1] + hex[1], 16);
        g = parseInt(hex[2] + hex[2], 16);
        b = parseInt(hex[3] + hex[3], 16);
      }
      // 6 digits hex
      else if (hex.length === 7) {
        r = parseInt(hex[1] + hex[2], 16);
        g = parseInt(hex[3] + hex[4], 16);
        b = parseInt(hex[5] + hex[6], 16);
      }

      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
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
