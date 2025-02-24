<template>
  <div class="frame-container">
    <div class="frame-title"><b>Generate</b> a Personalized Exploration Path Based on Your Skills & Interests 📍</div>

    <form @submit.prevent="handleUserPointGenerator" class="">
      <!-- Radio group and button in the same row -->
      <div class="flex items-center justify-between">
        <!-- Nuxt UI Radio Group with horizontal alignment -->
        <URadioGroup
          v-model="mode"
          legend=""
          :options="[
          { value: 'skills', label: 'skills' },
          { value: 'interests', label: 'interests' }
        ]"
          class="flex space-x-4"
        />

        <!-- Input field -->
        <div class="relative">
          <input
            v-model="inputValue"
            type="text"
            class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-500 focus-visible:ring-offset-2 placeholder:text-muted-foreground transition-colors duration-200"
            :placeholder="mode === 'skills' ? 'I work as a nurse' : 'I like to play the piano'"
          />
        </div>

        <!-- Submit button -->
        <UButton
          type="submit"
          color="primary"
          variant="solid"
          :loading="isLoading"
          :disabled="isLoading"
          class="w-auto"
        >
          {{ isLoading ? 'Processing...' : 'Calculate POI 📍' }}
          <template #trailing>
            <div v-if="isLoading">
              <i class="animate-spin i-heroicons-spinner"></i>
            </div>
          </template>
        </UButton>
      </div>
    </form>
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
          else if (gameStore.getLevel) {
            response = await getUserCoordinates({
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
