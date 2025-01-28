<template>
  <div class="mt-6 w-full max-w-4xl rounded-lg bg-white p-4 shadow-md">
    <!-- Explanation Section -->
    <div class="mb-4 text-sm text-gray-600">
      <p>Not sure which Sustainable Development Goal (SDG) aligns with your skills or interests? Enter your skills or interests below to get a suggestion! You can try both options for better insights.</p>
    </div>

    <div class="grid grid-flow-col grid-rows-1 gap-4">
      <!-- SDG Suggestion Interface Based on Skills -->
      <div class="col-span-1">
        <p class="mb-2 text-base font-medium text-gray-800">Find SDG Based on Your Skills</p>
        <input
          v-model="skillsInput"
          type="text"
          class="mb-2 w-full rounded-md border border-gray-300 p-2 text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="e.g., programming, problem-solving"
        />
        <button
          @click="handleGenerateSuggestion('skills')"
          class="w-full rounded-md bg-blue-500 px-3 py-2 text-sm font-medium text-white hover:bg-blue-600"
        >
          Get SDG Suggestion
        </button>
        <div v-if="proposedSdgFromSkills" class="mt-4 rounded-md bg-green-100 p-3 text-gray-800">
          <div v-if="proposedSdgFromSkills.proposedSdgId">
            <!-- SDG Icon Rendering -->
            <img
              v-if="sdgIconFromSkills"
              :src="`data:image/svg+xml;base64,${sdgIconFromSkills}`"
              :alt="`SDG ${proposedSdgFromSkills.proposedSdgId} Icon`"
              class="w-8 h-8 object-contain mt-2"
            />
          </div>
          <p><strong>SDG:</strong> {{ proposedSdgFromSkills.proposedSdgId }}</p>
          <p><strong>Reasoning:</strong> {{ proposedSdgFromSkills.reasoning }}</p>
        </div>
      </div>

      <!-- SDG Suggestion Interface Based on Interests -->
      <div class="col-span-1">
        <p class="mb-2 text-base font-medium text-gray-800">Find SDG Based on Your Interests</p>
        <input
          v-model="interestsInput"
          type="text"
          class="mb-2 w-full rounded-md border border-gray-300 p-2 text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="e.g., environment, education"
        />
        <button
          @click="handleGenerateSuggestion('interests')"
          class="w-full rounded-md bg-blue-500 px-3 py-2 text-sm font-medium text-white hover:bg-blue-600"
        >
          Get SDG Suggestion
        </button>
        <div v-if="proposedSdgFromInterests" class="mt-4 rounded-md bg-green-100 p-3 text-gray-800">
          <!-- SDG Icon Rendering -->
          <div v-if="proposedSdgFromInterests.proposedSdgId">
            <img
              v-if="sdgIconFromInterests"
              :src="`data:image/svg+xml;base64,${sdgIconFromInterests}`"
              :alt="`SDG ${proposedSdgFromInterests.proposedSdgId} Icon`"
              class="w-8 h-8 object-contain mt-2"
            />
          </div>
          <p><strong>SDG:</strong> {{ proposedSdgFromInterests.proposedSdgId }}</p>
          <p><strong>Reasoning:</strong> {{ proposedSdgFromInterests.reasoning }}</p>

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
      skillsInput: "",
      interestsInput: "",
    };
  },
  computed: {
    proposedSdgFromSkills() {
      return useGameStore().proposedSdgFromSkills;
    },
    proposedSdgFromInterests() {
      return useGameStore().proposedSdgFromInterests;
    },
    sdgIconFromSkills() {
      const sdgsStore = useSDGsStore();
      const sdgId = this.proposedSdgFromSkills?.proposedSdgId;

      if (sdgId && sdgsStore.sdgs.length > 0) {
        const sdg = sdgsStore.sdgs.find((goal) => goal.id === sdgId);
        return sdg ? sdg.icon : null;
      }
      return null;
    },
    sdgIconFromInterests() {
      const sdgsStore = useSDGsStore();
      const sdgId = this.proposedSdgFromInterests?.proposedSdgId;

      if (sdgId && sdgsStore.sdgs.length > 0) {
        const sdg = sdgsStore.sdgs.find((goal) => goal.id === sdgId);
        return sdg ? sdg.icon : null;
      }
      return null;
    },
  },
  methods: {
    async handleGenerateSuggestion(type) {
      const gameStore = useGameStore();
      const { proposeSdgBasedOnSkills, proposeSdgBasedOnInterests } = useGPTAssistantService();

      try {
        if (type === "skills" && this.skillsInput) {
          const response = await proposeSdgBasedOnSkills({
            skills: this.skillsInput,
          }); // Pass an object with "skills" key
          gameStore.setProposedSdgFromSkills(response);
        } else if (type === "interests" && this.interestsInput) {
          const response = await proposeSdgBasedOnInterests({
            interests: this.interestsInput,
          }); // Pass an object with "interests" key
          gameStore.setProposedSdgFromInterests(response);
        }
      } catch (error) {
        console.error("Error generating SDG suggestion:", error);
      }
    },
  },
};
</script>
