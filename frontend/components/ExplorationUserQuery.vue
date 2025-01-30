<template>
  <div class="mt-6 w-full max-w-4xl rounded-lg bg-white p-4 shadow-md">
    <!-- Mode Selection -->
    <div class="mb-4">
      <label class="block mb-2 text-base font-medium text-gray-800">Select Mode:</label>
      <div class="flex items-center gap-4">
        <input type="radio" id="modeSkills" value="skills" v-model="mode">
        <label for="modeSkills">Skills</label>
        <input type="radio" id="modeInterests" value="interests" v-model="mode">
        <label for="modeInterests">Interests</label>
      </div>
    </div>

    <!-- Input Field -->
    <div>
      <label class="block mb-2 text-base font-medium text-gray-800">Enter {{ mode === 'skills' ? 'Skills' : 'Interests' }}:</label>
      <input
        v-model="inputValue"
        type="text"
        class="w-full rounded-md border border-gray-300 p-2 text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
        :placeholder="mode === 'skills' ? 'e.g., programming, problem-solving' : 'e.g., environment, education'"
      />
    </div>

    <!-- Get Enriched Description Button -->
    <button
      @click="handleGetEnrichedDescription"
      class="mt-4 w-full rounded-md bg-blue-500 px-3 py-2 text-sm font-medium text-white hover:bg-blue-600"
    >
      Get Enriched Description
    </button>

    <!-- Display Enriched Description -->
    <div v-if="enrichedDescription" class="mt-4 rounded-md bg-green-100 p-3 text-gray-800">
      <p><strong>{{ mode === 'skills' ? 'Skills' : 'Interests' }}:</strong> {{ inputValue }}</p>
      <p><strong>Enriched Description:</strong> {{ enrichedDescription }}</p>
    </div>
  </div>
</template>

<script>
import useGPTAssistantService from "@/composables/useGPTAssistantService";
import { useGameStore } from "@/stores/game";

export default {
  data() {
    return {
      mode: "skills", // Default mode selection
      inputValue: "",
      enrichedDescription: "",
    };
  },
  methods: {
    async handleGetEnrichedDescription() {
      const { getSkillsDescription, getInterestsDescription } = useGPTAssistantService();
      const gameStore = useGameStore();
      const input = this.inputValue.trim();

      try {
        let response;
        if (this.mode === "skills" && input) {
          response = await getSkillsDescription({ skills: input });
          gameStore.setSkillsDescription(response);
        } else if (this.mode === "interests" && input) {
          response = await getInterestsDescription({ interests: input });
          gameStore.setInterestsDescription(response);
        }

        if (response) {
          this.enrichedDescription = response.enrichedDescription;
        } else {
          this.enrichedDescription = "No enriched description available.";
        }
      } catch (error) {
        console.error("Error fetching enriched description:", error);
        this.enrichedDescription = "Failed to fetch enriched description.";
      }
    },
  },
};
</script>

