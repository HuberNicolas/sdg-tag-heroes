<template>
  <div class="abstract-marking-page">
    <!-- Left side: Abstract Card -->
    <div class="abstract-card-container">
      <div class="abstract-card">
        <h2 class="text-xl font-bold mb-4">Abstract</h2>
        <p
          class="text-base text-justify"
          v-html="highlightedAbstract"
          @mouseup="handleTextSelection"
        ></p>
      </div>
    </div>

    <!-- Right side: Marked Text and Details -->
    <div class="details-container">
      <div class="details-card">
        <h2 class="text-xl font-bold mb-4">Details</h2>
        <div v-if="markedText">
          <h3 class="font-semibold mb-2">Selected Passage:</h3>
          <p class="marked-text">{{ markedText }}</p>
        </div>
        <div v-else>
          <p>No passage selected yet.</p>
        </div>

        <div class="form mt-4">
          <label class="block mb-2">
            <span class="text-sm font-medium">Proposed Label</span>
            <select v-model="proposedLabel" class="dropdown">
              <option disabled value="">Select a label</option>
              <option v-for="label in labels" :key="label" :value="label">
                {{ label }}
              </option>
            </select>
          </label>

          <label class="block mb-2">
            <span class="text-sm font-medium">Voted Label</span>
            <select v-model="votedLabel" class="dropdown">
              <option disabled value="">Select a label</option>
              <option v-for="label in labels" :key="label" :value="label">
                {{ label }}
              </option>
            </select>
          </label>

          <button
            class="confirm-button mt-4"
            @click="confirmSelection"
            :disabled="!markedText || !proposedLabel || !votedLabel"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useRuntimeConfig } from "nuxt/app";
import { usePublicationsStore } from "~/stores/publications";

const route = useRoute();
const publicationsStore = usePublicationsStore();
const config = useRuntimeConfig();

const loading = ref(true);
const error = ref<string | null>(null);
const publicationId = ref<number>(Number(route.params.id));
const publication = computed(() => publicationsStore.selectedPublication);

const markedText = ref("");
const proposedLabel = ref<string | null>(null);
const votedLabel = ref<string | null>(null);
const labels = ["1", "2", "3", "4", "5"]; // Example dropdown options for labels
const highlightedAbstract = computed(() => {
  if (!publication.value?.description || !markedText.value) {
    return publication.value?.description || "No abstract available.";
  }
  return publication.value.description.replace(
    markedText.value,
    `<mark class="highlight">${markedText.value}</mark>`
  );
});

// Fetch publication details
const fetchPublicationDetails = async () => {
  loading.value = true;
  error.value = null;

  try {
    await publicationsStore.fetchPublication(publicationId.value);
  } catch (err: any) {
    error.value = err.message || "Failed to fetch publication details.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchPublicationDetails);

// Handle text selection from the abstract
const handleTextSelection = () => {
  const selection = window.getSelection();
  if (selection) {
    const selectedText = selection.toString().trim();
    if (selectedText) {
      markedText.value = selectedText;
    }
  }
};

// Submit the form data to the API
const confirmSelection = async () => {
  const payload = {
    proposed_label: Number(proposedLabel.value),
    voted_label: Number(votedLabel.value),
    description: markedText.value,
  };

  try {
    const response = await $fetch(`${config.public.apiUrl}sdg_user_labels/publications/${publicationId.value}/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        "Content-Type": "application/json",
      },
      body: payload,
    });

    console.log("Submitted successfully:", response);
    // Reset inputs
    markedText.value = "";
    proposedLabel.value = null;
    votedLabel.value = null;
  } catch (err: any) {
    console.error("Submission failed:", err.message || err);
  }
};
</script>

<style scoped>
.abstract-marking-page {
  display: flex;
  gap: 1rem;
  height: 100vh;
  padding: 1rem;
  box-sizing: border-box;
}

.abstract-card-container {
  width: 50%;
  padding: 1rem;
  box-sizing: border-box;
}

.details-container {
  width: 50%;
  padding: 1rem;
  box-sizing: border-box;
}

.abstract-card,
.details-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  height: 100%;
}

.highlight {
  background-color: yellow;
  font-weight: bold;
}

.marked-text {
  background-color: #f0f0f0;
  padding: 0.5rem;
  border-radius: 4px;
  font-style: italic;
}

.dropdown {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.confirm-button {
  background-color: #007bff;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-button:disabled {
  background-color: #ddd;
  cursor: not-allowed;
}
</style>
