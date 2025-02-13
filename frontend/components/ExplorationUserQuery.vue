<template>
  <form @submit.prevent="handleUserPointGenerator" class="max-w-md mx-auto space-y-6 bg-card rounded-lg shadow-sm p-6">
    <!-- Radio group -->
    <div class="flex items-center space-x-4">
      <label class="text-sm font-medium text-muted-foreground">Mode:</label>
      <label v-for="option in ['skills', 'interests']"
             :key="option"
             class="flex items-center space-x-2 cursor-pointer">
        <input
          type="radio"
          :value="option"
          :checked="mode === option"
          @change="mode = $event.target.value"
          class="w-4 h-4 border-gray-300 focus:ring-2 focus:ring-primary rounded-full"
        >
        <span class="text-sm">{{ option }}</span>
      </label>
    </div>

    <!-- Input field -->
    <div class="relative">
      <input v-model="inputValue"
             type="text"
             class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 placeholder:text-muted-foreground transition-colors duration-200"
             :placeholder="mode === 'skills' ? 'e.g., programming, problem-solving' : 'e.g., environment, education'"
      />
    </div>

    <!-- Submit button with loading state -->
    <!-- icon="mdi-map-marker-outline" -->
    <UButton
    type="submit"
    color="primary"
    variant="solid"
    :loading="isLoading"
    :disabled="isLoading"
    class="w-full"
  >

    <!-- Button text -->
      {{ isLoading ? 'Processing...' : 'Calculate Point of Interest 📍' }}

      <!-- Trailing loading indicator -->
      <template #trailing>
        <div v-if="isLoading">
          <i class="animate-spin i-heroicons-spinner"></i>
        </div>
      </template>
    </UButton>
  </form>
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
      isLoading: false
    };
  },
  methods: {
    async handleUserPointGenerator() {
      this.isLoading = true; // Set loading state

      try {
        const { getSkillsDescription, getInterestsDescription, getUserCoordinates } = useGPTAssistantService();
        const gameStore = useGameStore();
        const input = this.inputValue.trim();

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

          if (gameStore.getSDG && gameStore.getLevel) {
            response = await getUserCoordinates({
              sdg: gameStore.getSDG,
              level: gameStore.getLevel,
              userQuery: response.enrichedDescription});
            gameStore.setUserCoordinates(response);
          }
        } else {
          this.enrichedDescription = "No enriched description available.";
        }
      } catch (error) {
        console.error("Error fetching enriched description:", error);
        this.enrichedDescription = "Failed to fetch enriched description.";
      } finally {
        this.isLoading = false; // Reset loading state
      }
    },
  },
};
</script>

