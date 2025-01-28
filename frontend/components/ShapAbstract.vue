<template>
  <div class="container mx-auto p-4">
    <!-- Publication Title -->
    <h1 class="text-2xl font-bold mb-4">{{ publication?.title }}</h1>

    <!-- Toggle for SHAP/Plain Text -->
    <div class="mb-6">
      <label class="inline-flex items-center">
        <input
          type="checkbox"
          v-model="showShap"
          class="form-checkbox h-5 w-5 text-blue-600"
        />
        <span class="ml-2 text-gray-700">Show SHAP Highlights</span>
      </label>
    </div>

    <!-- Abstract Display -->
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-xl font-semibold mb-4">Abstract</h2>
      <div v-if="showShap && explanation" class="text-justify"
           v-html="shapHighlightedAbstract"
           @mouseup="handleAbstractSelection">
      </div>
      <div v-else class="text-justify text-gray-700">
        {{ publication?.description || "No abstract available." }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useExplanationsStore } from "~/stores/explanations";
import { usePublicationsStore } from "~/stores/publications";
import { useSDGsStore } from "~/stores/sdgs";
import * as d3 from "d3";

const route = useRoute();
const explanationStore = useExplanationsStore();
const publicationsStore = usePublicationsStore();
const sdgsStore = useSDGsStore();

const publicationId = computed(() => Number(route.params.publicationId));
const publication = computed(() => publicationsStore.publicationDetails);
const explanation = computed(() => explanationStore.explanation);

const sdgs = Array.from({ length: 17 }, (_, i) => i + 1); // SDGs 1-17
const showShap = ref(true); // Toggle for SHAP highlights

// Use the selected SDG from the store
const selectedSDG = computed({
  get: () => sdgsStore.getSelectedSDG,
  set: (value) => sdgsStore.setSelectedSDG(value),
});

// Fetch publication, explanation, and SDGs on mount
onMounted(async () => {
  await publicationsStore.fetchPublicationById(publicationId.value);
  await explanationStore.fetchExplanationByPublicationId(publicationId.value);
  await sdgsStore.fetchSDGs();
});

// Watch for changes in selected SDG and fetch SHAP explanations
watch(selectedSDG, async () => {
  if (publicationId.value) {
    await explanationStore.fetchExplanationByPublicationId(publicationId.value);
  }
});

// Compute SHAP-highlighted abstract
const shapHighlightedAbstract = computed(() => {
  if (!explanation.value || !publication.value?.description) return "";

  const { inputTokens, tokenScores, baseValues } = explanation.value;
  const sdgIndex = selectedSDG.value - 1; // SDG index (0-based)

  // Adjust token scores for the selected SDG
  const adjustedScores = tokenScores.map((scores) => scores[sdgIndex]);

  // Highlight tokens based on their SHAP scores
  return highlightTextTokens(inputTokens, adjustedScores, publication.value.description);
});

// Helper function to highlight tokens in the abstract
const highlightTextTokens = (tokens: string[], scores: number[], text: string) => {
  const threshold = 0.0001; // Ignore negligible SHAP scores
  const highlightedText: string[] = [];
  let remainingText = text;

  // Get the selected SDG color
  const selectedSDGColor = sdgsStore.sdgs.find(sdg => sdg.id === selectedSDG.value)?.color || "#ffff00";
  const negativeColor = "#7D7D7D";

  // Get the min and max scores
  const maxScore = Math.max(0, Math.max(...scores));
  const minScore = Math.min(0, Math.min(...scores));

  // Create the color scale according to the min and max scores
  const colorScale = d3.scaleLinear<string>()
    .domain([0, maxScore])
    .range(["#ffffff", selectedSDGColor]);
  const negColorScale = d3.scaleLinear<string>()
    .domain([0, -minScore])
    .range(["#ffffff", negativeColor]);

  tokens.forEach((token, index) => {
    const score = scores[index];
    if (Math.abs(score) < threshold) return;

    // Match the token in the remaining text
    const tokenRegex = new RegExp(`\\b${token.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, "i");
    const match = remainingText.match(tokenRegex);

    if (!match) return;

    const idxStart = match.index!;
    const idxEnd = idxStart + token.length;

    // Add plain text before the token
    highlightedText.push(remainingText.substring(0, idxStart));

    // Add highlighted token
    const highlightColor = score > 0 ? rgbToHex(colorScale(score)) : rgbToHex(negColorScale(-score));
    highlightedText.push(`<mark style="background-color: ${highlightColor}; padding: 0;">${remainingText.substring(idxStart, idxEnd)}</mark>`);

    // Remove the processed part of the text
    remainingText = remainingText.slice(idxEnd);
  });

  highlightedText.push(remainingText); // Add any remaining plain text
  return highlightedText.join("");
};

// Convert RGB to Hex
const rgbToHex = (rgb: string) => {
  if (!rgb) return "#ffffff";
  const [r, g, b] = rgb.slice(4, -1).split(',').map(Number);
  return '#' + [r, g, b].map(component => {
    const hex = component.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
};

const handleAbstractSelection = () => {
  const selection = window.getSelection();
  if (selection && selection.toString().trim() !== "") {
    const selectedText = selection.toString().trim();
    explanationStore.setMarkedText(selectedText); // Update the store
  }
};
</script>
