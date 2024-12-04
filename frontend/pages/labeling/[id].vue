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

    <!-- Bottom Section: Scrollable Labels -->
    <div class="labels-section">
      <h2 class="text-xl font-bold mb-4">Existing Labels</h2>
      <div v-if="labelsLoading" class="loading">Loading labels...</div>
      <div v-if="labelsError" class="error">{{ labelsError }}</div>
      <div v-if="!labelsLoading && !labelsError && userLabels.length > 0" class="scrollable-labels">
        <div v-for="label in userLabels" :key="label.label_id" class="label-card">
          <p><strong>Proposed Label:</strong> {{ label.proposed_label }}</p>
          <p><strong>Voted Label:</strong> {{ label.voted_label }}</p>
          <p><strong>Description:</strong> {{ label.description }}</p>
          <p><strong>Label Date:</strong> {{ formatDate(label.labeled_at) }}</p>
        </div>
      </div>
      <p v-else>No labels found.</p>
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
const labels = ["1", "2", "3", "4", "5"];
const highlightedAbstract = computed(() => {
  if (!publication.value?.description || !markedText.value) {
    return publication.value?.description || "No abstract available.";
  }
  return publication.value.description.replace(
    markedText.value,
    `<mark class="highlight">${markedText.value}</mark>`
  );
});

// Labels Data
const userLabels = ref([]);
const labelsLoading = ref(false);
const labelsError = ref<string | null>(null);

const fetchLabels = async () => {
  labelsLoading.value = true;
  labelsError.value = null;

  try {
    const response = await $fetch(`${config.public.apiUrl}sdg_user_labels/publications/${publicationId.value}/labels`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });
    userLabels.value = response;
  } catch (err: any) {
    labelsError.value = err.message || "Failed to load labels.";
  } finally {
    labelsLoading.value = false;
  }
};

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
    fetchLabels();
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
    fetchLabels(); // Refresh labels after submission
    markedText.value = "";
    proposedLabel.value = null;
    votedLabel.value = null;
  } catch (err: any) {
    console.error("Submission failed:", err.message || err);
  }
};

// Format dates for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};
</script>

<style scoped>
.abstract-marking-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100vh;
  padding: 1rem;
  box-sizing: border-box;
}

.abstract-card-container {
  width: 50%;
  padding: 1rem;
}

.details-container {
  width: 50%;
  padding: 1rem;
}

.labels-section {
  margin-top: 2rem;
}

.scrollable-labels {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 8px;
}

.label-card {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
}

.loading {
  text-align: center;
  color: #888888;
}

.error {
  color: red;
  text-align: center;
}

.highlight {
  background-color: yellow;
  font-weight: bold;
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
  color: white;
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
