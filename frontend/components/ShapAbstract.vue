<template>
  <div class="frame-container h-full flex flex-col">
    <!-- Frame Title with ShapToggle -->
    <div class="frame-title flex justify-between items-center">
      <span><b>Compare</b> Machine-Generated Highlights vs. Full Abstract</span>
      <ShapToggle />
    </div>

    <div class="p-1 flex-1 min-h-0 flex flex-col overflow-hidden">
      <!-- Abstract Display -->
      <div
class="bg-surface-2/70 border border-line p-4 rounded-xl flex flex-col h-full overflow-hidden"
           @mouseup="handleAbstractSelection">
        <LoadingState v-if="!publication" label="loading abstract" class="flex-1" />
        <template v-else>
          <h1 class="text-[1.35rem] leading-snug font-bold tracking-tight mb-3">{{ publication.title }}</h1>
          <div class="flex-1 overflow-y-auto text-[17px] leading-[1.75] text-fg/90 pr-1">
            <!-- eslint-disable-next-line vue/no-v-html -- the text is escaped, only the <mark> tags are HTML -->
            <span v-html="shapHighlightedAbstract"/>
          </div>
        </template>
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

// Highlights fade from the page background into the SDG colour, so they also work in dark mode
const colorMode = useColorMode();
const highlightBase = computed(() => (colorMode.value === "dark" ? "#0e0e15" : "#ffffff"));


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

  if (!explanation.value || !showShap.value) return escapeHtml(description);

  const { inputTokens, tokenScores } = explanation.value;
  if (!inputTokens || !tokenScores) return escapeHtml(description);

  const sdgIdx = selectedSDG.value - 1; // Convert to 0-based index
  const scoresForSelectedSDG = tokenScores.map((scores) => Math.max(0, scores[sdgIdx]));

  const maxScore = Math.max(0, ...scoresForSelectedSDG);

  // Get the selected SDG color (fallback to yellow)
  const selectedSDGColor =
    sdgsStore.sdgs.find((sdg) => sdg.id === selectedSDG.value)?.color || "#ffff00";

  // Create a d3 color scale
  const colorScale = d3.scaleLinear<string>()
    .domain([0, maxScore])
    .range([highlightBase.value, selectedSDGColor]);

  let remainingText = description;
  const highlightedParts: string[] = [];

  // Loop sequentially over each token and its score
  inputTokens.forEach((token, index) => {
    const score = scoresForSelectedSDG[index];
    if (score <= 0) return; // Skip tokens below threshold

    const idx = remainingText.indexOf(token);
    if (idx === -1) return;

    // Append un-highlighted text before the token
    highlightedParts.push(escapeHtml(remainingText.slice(0, idx)));

    // Determine the highlight color
    const highlightColor = rgbToHex(colorScale(score));

    // Append highlighted token
    highlightedParts.push(
      `<mark style="background-color: ${highlightColor}; color: inherit; padding: 0 1px; border-radius: 3px;">${escapeHtml(token)}</mark>`
    );

    // Remove the processed part from the text
    remainingText = remainingText.slice(idx + token.length);
  });

  // Append remaining text after last token
  highlightedParts.push(escapeHtml(remainingText));

  return highlightedParts.join("");
});


// The abstract is rendered with v-html (for the <mark> highlights), so its text must be escaped
const escapeHtml = (text: string) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");

// Helper function to convert an "rgb(…)" string to a hex color code.
// This is essentially the same as your previous rgbToHex.
const rgbToHex = (rgb: string) => {
  // No colour (e.g. no SDG selected yet): no highlight instead of a white box
  if (!rgb) return "transparent";
  const rgbValues = rgb.match(/\d+/g);
  if (!rgbValues) return "transparent";
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
