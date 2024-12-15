<template>
  <div class="abstract-marking-page">
    <SDGSelection></SDGSelection>

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
    <!-- SHAP-Highlighted Abstract -->
    <div class="abstract-card-container">
      <div class="abstract-card">
        <h2 class="text-xl font-bold mb-4">
          SHAP-Highlighted Abstract
          <span v-if="selectedSDG">(SDG {{ selectedSDG }})</span>
        </h2>
        <p
          v-if="selectedSDG"
          class="text-base text-justify"
          v-html="shapHighlightedAbstract"
        ></p>
        <p
          v-else
          class="text-gray-500 text-center italic"
        >
          Please select an SDG to display the SHAP-highlighted abstract.
        </p>
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

        <div>
          <h3 class="font-semibold mb-2">Write Comment:</h3>
          <UTextarea v-model="comment" />
        </div>

        <div class="form mt-4">
        <!--
          <label class="block mb-2">
            <span class="text-sm font-medium">Proposed Label</span>
            <select v-model="proposedLabel" class="dropdown">
              <option disabled value="">Select a label</option>
              <option v-for="label in labels" :key="label" :value="label">
                {{ label }}
              </option>
            </select>
          </label>
          -->

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
            :disabled="!votedLabel"
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
          <p><strong>Abstract Selection:</strong> {{ label.abstract_section }}</p>
          <p><strong>Comment</strong> {{ label.comment }}</p>
          <p><strong>Label Date:</strong> {{ formatDate(label.labeled_at) }}</p>
        </div>
      </div>
      <p v-else>No labels found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3';
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
const comment = ref("");
const proposedLabel = ref<string | null>(null);
const votedLabel = ref<string | null>(null);
const labels = [...Array(18).keys()];
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


import { useSDGStore } from '@/stores/sdgs';

const sdgStore = useSDGStore();
const selectedSDG = computed(() => sdgStore.selectedGoal); // Dynamically selected SDG
const shapHighlightedAbstract = ref<string | null>(null);

// Fetch publication details
const fetchPublicationDetails = async () => {
  loading.value = true;
  error.value = null;

  try {
    await publicationsStore.fetchPublication(publicationId.value);

    // Fetch SHAP explanations after fetching the publication
    await fetchShapExplanations(publication.value?.publication_id);
  } catch (err: any) {
    error.value = err.message || "Failed to fetch publication details.";
  } finally {
    loading.value = false;
    fetchLabels();
  }
};

// Fetch SHAP explanations
const fetchShapExplanations = async (publication_id: number | undefined) => {
  if (!publication_id) return;

  try {
    const response = await $fetch(
      `${config.public.apiUrl}explanations/publications/${publication_id}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      }
    );

    // Process the SHAP explanation to highlight tokens
    const { input_tokens, token_scores, base_values } = response;

    console.log(input_tokens, token_scores, base_values);

    // Fetch the weight (probability for the selected SDG)
    const weight = base_values[0] // NOT USED YET

    // Adjust the scores dynamically for the selected SDG
    const adjustedScores = adjustTokenScoresWithBaseValues(
      token_scores,
      base_values,
      selectedSDG.value - 1, // SDG index (0-based)
      weight
    );
    const goalColor = sdgStore.getSelectedGoalColor(selectedSDG.value); // Fetch color dynamically

    // Create color scales for highlighting
    const maxScore = Math.max(0, Math.max(...adjustedScores));
    const minScore = Math.min(0, Math.min(...adjustedScores));
    const colorScale = d3.scaleLinear<string>().domain([0, maxScore]).range(["#ffffff", goalColor || "#ffffff"]);
    const negColorScale = d3.scaleLinear<string>().domain([0, -minScore]).range(["#ffffff", "#7D7D7D"]); // Grey for negatives
    // Highlight the tokens in the abstract
    const shapHtml = highlightTextTokens(input_tokens, adjustedScores, publication.value?.description || "", colorScale, negColorScale);

    shapHighlightedAbstract.value = shapHtml;
  } catch (err: any) {
    console.error("Failed to fetch SHAP explanations:", err.message || err);
  }
};

const highlightTextTokens = (tokens: string[], scores: number[], text: string, colorScale: any, negColorScale: any) => {
  const threshold = 0.0000001; // Small threshold to ignore negligible SHAP scores
  const highlightedText: string[] = [];
  let remainingText = text;
  console.log(text)
  console.log(tokens)
  console.log(scores)

  tokens.forEach((token, index) => {
    const score = scores[index];
    if (Math.abs(score) < threshold) return; // Skip tokens with near-zero scores

    // Use a regex to match the token at the start of the remaining text
    const tokenRegex = new RegExp(`\\b${token.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, "i");
    const match = remainingText.match(tokenRegex);

    if (!match) return; // Skip if token is not found

    const idxStart = match.index!;
    const idxEnd = idxStart + token.length;

    const color = score > 0 ? colorScale(score) : negColorScale(-score);

    // Add plain text before the token
    highlightedText.push(remainingText.substring(0, idxStart));
    // Add highlighted token
    highlightedText.push(`<span style="background-color:${color}">${remainingText.substring(idxStart, idxEnd)}</span>`);

    // Remove the processed part of the text
    remainingText = remainingText.slice(idxEnd);
  });

  highlightedText.push(remainingText); // Add any remaining plain text
  return highlightedText.join("");
};



const adjustTokenScoresWithBaseValues = (scores: number[][], baseValues: number[], sdgIndex: number, weight: number) => {
  return scores.map((scoreArray, tokenIndex) => {
    const baseValue = baseValues[tokenIndex] || 0; // Ensure baseValue exists
    //const adjustedScore = scoreArray.map((score) => (score - baseValue) * weight); // Apply weight
    const adjustedScore = scoreArray.map((score) => (score - 0) * 1); // Apply weight
    return adjustedScore[sdgIndex]; // Only return the score for the selected SDG
  });
};

// Watch for changes in selectedSDG and ensure it’s defined
watchEffect(() => {
  if (selectedSDG.value && publication.value?.publication_id) {
    fetchShapExplanations(publication.value.publication_id);
  }
});

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

const confirmSelection = async () => {
  const payload = {
    voted_label: Number(votedLabel.value),
    abstract_section: markedText.value,
    comment: comment.value,
  };

  try {
    // Submit the annotation first
    const annotationResponse = await $fetch(
      `${config.public.apiUrl}sdg_user_labels/publications/${publicationId.value}/`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: payload,
      }
    );

    console.log("Annotation submitted successfully:", annotationResponse);

    // Evaluate the annotation score
    const scorePayload = {
      passage: markedText.value,
      annotation: comment.value,
      sdg_label: votedLabel.value,
    };

    const scoreResponse = await $fetch(
      `${config.public.apiUrl}annotations/score`, // Adjust the endpoint path as necessary
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: scorePayload,
      }
    );

    console.log("Score evaluated successfully:", scoreResponse);

    // Extract relevant details for the bank increment
    const bankIncrementPayload = {
      increment: scoreResponse.combined_score, // Use the combined score as the increment
      sdg: `SDG_${votedLabel.value}`, // Convert voted label to SDG format (e.g., "SDG_17")
      reason: scoreResponse.reasoning, // Reason for the increment
    };


    const bankIncrementResponse = await $fetch(
      `${config.public.apiUrl}banks/history`, // Adjust the endpoint path as necessary
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: bankIncrementPayload,
      }
    );

    console.log("Bank increment added successfully:", bankIncrementResponse);

    // Display a toast with the XP gained
    toast.add({
      //title: "XP Gained!",
      title: `You earned ${bankIncrementPayload.increment} XP for your annotation.`,
      type: "success",
      timeout: 5000,
    });

    // Refresh labels and reset fields after submission
    fetchLabels();
    markedText.value = "";
    comment.value = "";
    proposedLabel.value = null;
    votedLabel.value = null;
  } catch (err: any) {
    console.error("Submission or scoring failed:", err.message || err);
  }
};


// Format dates for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

const toast = useToast()

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
