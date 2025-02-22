<template>
  <div class="frame-container h-full flex flex-col">
    <!-- Frame Title with ShapToggle -->
    <div class="frame-title flex justify-between items-center">
      <span><b>Read Publication</b> either with or without Machine Explanations</span>
      <ShapToggle />
    </div>

    <div class="container mx-auto p-1 flex-1 flex flex-col overflow-hidden">
      <!-- Abstract Display -->
      <div class="bg-white p-4 rounded-lg shadow-md flex flex-col h-full overflow-hidden"
           @mouseup="handleAbstractSelection">
        <h1 class="text-xl font-bold mb-1">{{ publication?.title }}</h1>
        <div class="flex-1 overflow-y-auto text-justify">
          <span v-html="shapHighlightedAbstract"></span>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { computed, watch, onMounted } from "vue";
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
const showShap = computed(() => explanationStore.showShap);

const sdgs = Array.from({ length: 17 }, (_, i) => i + 1); // SDGs 1-17

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
  // Ensure we always have a description
  const description = publication.value?.description || "No abstract available.";

  if (!explanation.value || !showShap.value) return description;

  const { inputTokens, tokenScores } = explanation.value;
  if (!inputTokens || !tokenScores) return description;

  const sdgIdx = selectedSDG.value - 1; // Convert to 0-based index
  const scoresForSelectedSDG = tokenScores.map((scores) => Math.max(0, scores[sdgIdx]));

  const maxScore = Math.max(0, ...scoresForSelectedSDG);

  // Get the selected SDG color (fallback to yellow)
  const selectedSDGColor =
    sdgsStore.sdgs.find((sdg) => sdg.id === selectedSDG.value)?.color || "#ffff00";

  // Create a d3 color scale
  const colorScale = d3.scaleLinear<string>()
    .domain([0, maxScore])
    .range(["#ffffff", selectedSDGColor]);

  let remainingText = description;
  const highlightedParts: string[] = [];

  // Loop sequentially over each token and its score
  inputTokens.forEach((token, index) => {
    const score = scoresForSelectedSDG[index];
    if (score <= 0) return; // Skip tokens below threshold

    const idx = remainingText.indexOf(token);
    if (idx === -1) return;

    // Append un-highlighted text before the token
    highlightedParts.push(remainingText.slice(0, idx));

    // Determine the highlight color
    const highlightColor = rgbToHex(colorScale(score));

    // Append highlighted token
    highlightedParts.push(
      `<mark style="background-color: ${highlightColor}; padding: 0;">${token}</mark>`
    );

    // Remove the processed part from the text
    remainingText = remainingText.slice(idx + token.length);
  });

  // Append remaining text after last token
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
