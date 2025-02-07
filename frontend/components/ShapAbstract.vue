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
      <div
        v-if="showShap && explanation"
        class="text-justify"
        v-html="shapHighlightedAbstract"
        @mouseup="handleAbstractSelection"
      ></div>
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

// Watch for changes in the selected SDG and re-fetch explanations
watch(selectedSDG, async () => {
  if (publicationId.value) {
    await explanationStore.fetchExplanationByPublicationId(publicationId.value);
  }
});

/*
  Compute the SHAP-highlighted abstract.
  This version uses a sequential token matching approach similar to your previous version:
  1. We extract the token scores for the selected SDG.
  2. We compute a d3 color scale (from white to the selected SDG color) based on the maximum positive score.
  3. We loop over the tokens in order. For each token, we use indexOf to find it in the remaining text,
     append the preceding plain text and then the highlighted token, and finally slice the text.
*/
const shapHighlightedAbstract = computed(() => {
  if (!explanation.value || !publication.value?.description)
    return publication.value?.description || "";

  const { inputTokens, tokenScores } = explanation.value;
  const sdgIdx = selectedSDG.value - 1; // convert to 0-based index
  const scoresForSelectedSDG = tokenScores.map((scores) => scores[sdgIdx]);
  console.log(scoresForSelectedSDG);

  // Compute the maximum positive score (previous version used Math.max(0, ...))
  const maxScore = Math.max(0, ...scoresForSelectedSDG);

  // Get the selected SDG color (or fallback to yellow)
  const selectedSDGColor =
    sdgsStore.sdgs.find((sdg) => sdg.id === selectedSDG.value)?.color ||
    "#ffff00";

  // Create a d3 color scale: tokens with a higher positive score get a stronger highlight
  const colorScale = d3.scaleLinear<string>()
    .domain([0, maxScore])
    .range(["#ffffff", selectedSDGColor]);

  const threshold = 0; // Only tokens with a score > 0 are highlighted
  let remainingText = publication.value.description;
  const highlightedParts: string[] = [];

  // Loop sequentially over each token and its score
  inputTokens.forEach((token, index) => {
    const score = scoresForSelectedSDG[index];
    if (score <= threshold) return; // skip tokens below threshold

    // Find the token in the remaining text (this approach mimics the previous version)
    const idx = remainingText.indexOf(token);
    if (idx === -1) return; // if not found, skip

    // Append text before the token (un-highlighted)
    highlightedParts.push(remainingText.slice(0, idx));

    // Determine the highlight color
    const highlightColor =
      score > threshold ? rgbToHex(colorScale(score)) : "#ffffff";

    // Append the token wrapped in a <mark> tag with the chosen styling.
    // (Here we use 14px and Roboto as in your previous version.)
    highlightedParts.push(
      `<mark style="background-color: ${highlightColor}; font-size: 14px; padding: 0;">${token}</mark>`
    );

    // Remove the processed part from the text
    remainingText = remainingText.slice(idx + token.length);
  });
  // Append any text that remains after the last token
  highlightedParts.push(remainingText);

  return highlightedParts.join("");
});

// Helper function to convert an "rgb(…)" string to a hex color code.
// This is essentially the same as your previous rgbToHex.
const rgbToHex = (rgb: string) => {
  if (!rgb) return "#ffffff";
  const rgbValues = rgb.match(/\d+/g);
  if (!rgbValues) return "#ffffff";
  return (
    "#" +
    rgbValues
      .slice(0, 3)
      .map((num) => {
        const hex = parseInt(num).toString(16);
        return hex.length === 1 ? "0" + hex : hex;
      })
      .join("")
  );
};

const handleAbstractSelection = () => {
  const selection = window.getSelection();
  if (selection && selection.toString().trim() !== "") {
    const selectedText = selection.toString().trim();
    explanationStore.setMarkedText(selectedText); // Update the store accordingly
  }
};
</script>
