<template>
  <div class="grid grid-cols-9 gap-4">

    <div class="col-span-1 justify-around">
      <HexGrid class="place-self-center"/>
    </div>

    <div class="col-span-8">
      <SDGSelection></SDGSelection>
    </div>

    <!-- Raw abstract Abstract -->
    <div class="col-span-3">

      <p v-if="publication">{{ publication.title }}</p>
      <br>
      <p
        class="text-base text-justify"
        v-html="highlightedAbstract"
        @mouseup="handleTextSelection"
        :style="{ '--highlight-color': sdgStore.getSelectedGoalColor(selectedSDG) || '#E5243B' }"
      ></p>
    </div>

    <!-- SHAP-Highlighted Abstract -->
    <div class="col-span-3">
      <div>
        <h1>
          SHAP-Highlighted Abstract
          <span v-if="selectedSDG">(SDG {{ selectedSDG }})</span>
        </h1>
        <br>
        <br>
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




    <div class="col-span-3">
      <p>Voting</p>
      <div>
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

          <UButton
            @click="confirmSelection"
            :disabled="!votedLabel"
          >
            Submit
          </UButton>
        </div>
      </div>
    </div>
    <div class="col-span-9">
      <UDivider></UDivider>
    </div>

    <!-- Comments Section -->
    <div class="col-span-6 max-h-96 overflow-y-auto pr-2">
      <div v-for="label in userLabels" :key="label.label_id" class="border-b border-gray-200 pb-4 mb-4">
        <!-- Existing Comment Code -->
        <div class="flex items-start gap-4">

          <div class="w-10 h-10 rounded-full flex-shrink-0">
            <img
              :src="generateUserAvatar(label.user_email)"
              alt="User Avatar"
              class="w-full h-full rounded-full"
            />
          </div>
          <div class="flex-1">
            <!-- Display Commenter's Email and Voted Label -->
            <p class="text-sm font-semibold text-gray-800">
              <span class="text-gray-600">{{ label.user_email }}</span> voted:
              <div class="flex items-center gap-2">
                <!-- SDG Icon -->
                <img
                  v-if="getSDGIcon(label.voted_label)"
                  :src="`data:image/svg+xml;base64,${getSDGIcon(label.voted_label)}`"
                  :alt="`SDG ${label.voted_label} Icon`"
                  class="w-6 h-6"
                />
                <!-- SDG Label (Fallback if no icon exists) -->
                <span class="font-medium">SDG {{ label.voted_label }}</span>
              </div>

            </p>

            <!-- Abstract Section -->
            <p class="text-sm text-gray-700 mt-1">
              <span class="font-medium text-gray-600">Abstract Selection:</span> {{ label.abstract_section }}
            </p>

            <!-- Comment -->
            <p class="text-sm text-gray-700 mt-1">
              <span class="font-medium text-gray-600">Comment:</span> {{ label.comment }}
            </p>

            <!-- Label Date -->
            <p class="text-xs text-gray-500 mt-1">
              <span class="font-medium">Label Date:</span> {{ formatDate(label.labeled_at) }}
            </p>
            <div class="flex items-center gap-4 mt-2 text-gray-600 text-sm">
              <p><strong>👍 Upvotes:</strong> {{ calculateVotes(label, 'positive') }}</p>
              <p><strong>👎 Downvotes:</strong> {{ calculateVotes(label, 'negative') }}</p>
              <p><strong>Score:</strong> {{ calculateScore(label) }}</p>
            </div>
            <div class="flex items-center gap-2 mt-2">
              <button
                @click="castVote(label.label_id, 'positive', 5.0)"
                :disabled="label.user_voted"
                class="flex items-center justify-center text-white bg-green-500 hover:bg-green-600 disabled:bg-gray-300 px-3 py-1 rounded"
              >
                👍 Upvote
              </button>
              <button
                @click="castVote(label.label_id, 'negative', -1.0)"
                :disabled="label.user_voted"
                class="flex items-center justify-center text-white bg-red-500 hover:bg-red-600 disabled:bg-gray-300 px-3 py-1 rounded"
              >
                👎 Downvote
              </button>
            </div>
            <p v-if="label.user_voted" class="text-xs text-gray-500 mt-1 italic">
              You have already voted for this label.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart Containers -->
    <div class="col-span-3">
      <div id="chart-container"></div>
      <div id="filtered-chart-container"></div>
    </div>





  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3';
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useRuntimeConfig } from "nuxt/app";
import { usePublicationsStore } from "~/stores/publications";
import {useUserStore} from "~/stores/user";
import UseAuth from '~/composables/useAuth';
import useAvatar from "~/composables/useAvatar";

const { generateAvatar } = useAvatar();

const generateUserAvatar = (email: string) => {
  return generateAvatar({ seed: email, size: 64 }).toDataUri();
};



// Refetch XP after successful annotation via emits
const emit = defineEmits(["xp-updated"])


const route = useRoute();
const publicationsStore = usePublicationsStore();
const userStore = useUserStore();
const config = useRuntimeConfig();

const user = ref<{ email: string } | null>(null);

const loading = ref(true);
const error = ref<string | null>(null);
const publicationId = ref<number>(Number(route.params.id));
const publication = computed(() => publicationsStore.selectedPublication);

const markedText = ref("");
const comment = ref("");
const proposedLabel = ref<string | null>(null);
const votedLabel = ref<string | null>(null);
const labels = [ ...Array(17).keys() ].map( i => i+1);
const highlightedAbstract = computed(() => {
  if (!publication.value?.description || !markedText.value) {
    return publication.value?.description || "No abstract available.";
  }
  const highlightColor = sdgStore.getSelectedGoalColor(selectedSDG.value) || "#E5243B";

  return publication.value.description.replace(
    markedText.value,
    `<span class="highlight" style="background-color: ${highlightColor};">${markedText.value}</span>`
  );
});

const getSDGIcon = (votedLabel: number) => {
  // Ensure goals.items exists and is an array
  const goalsArray = Array.isArray(sdgStore.goals.items) ? sdgStore.goals.items : [];
  const sdgGoal = goalsArray.find((goal) => goal.id === votedLabel);
  return sdgGoal?.icon || null; // Return icon or fallback to null
};

// Fetch user profile and generate avatar
const fetchUserProfile = async () => {
  try {
    const authService = new UseAuth();
    user.value = await authService.getProfile(); // Fetch user profile (e.g., email)
  } catch (error) {
    console.error("Error fetching user profile:", error);
  } finally {
    loading.value = false; // Set loading to false once complete
  }
};

// Labels Data
const userLabels = ref([]);
const labelsLoading = ref(false);
const labelsError = ref<string | null>(null);
const labelSubmitted = ref(false); // Tracks if a label has been submitted

const fetchLabels = async () => {
  labelsLoading.value = true;
  labelsError.value = null;

  try {
    // Fetch user labels
    const labelsResponse = await $fetch(
      `${config.public.apiUrl}sdg_user_labels/publications/${publicationId.value}/labels`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      }
    );

    // Extract unique user IDs
    const userIds = [...new Set(labelsResponse.map(label => label.user_id))];

    // Fetch user details for those user IDs
    const userDetailsResponse = await $fetch(`${config.public.apiUrl}users`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        "Content-Type": "application/json",
      },
      body: { user_ids: userIds },
    });

    // Map user details by user_id for quick lookup
    const userMap = new Map(userDetailsResponse.map(user => [user.user_id, user.email]));

    // Merge user emails into labels
    userLabels.value = labelsResponse.map(label => ({
      ...label,
      user_email: userMap.get(label.user_id) || "Unknown", // Add email or fallback
      user_voted: label.votes.some(vote => vote.user_id === userStore.user?.id),
    }));

    // Update charts
    createBarChart(userLabels.value);
    createFilteredBarChart(userLabels.value);
  } catch (err: any) {
    labelsError.value = err.message || "Failed to load labels.";
  } finally {
    labelsLoading.value = false;
  }
};



import { useSDGStore } from '@/stores/sdgs';
import HexGrid from "~/components/HexGrid.vue";

const sdgStore = useSDGStore();
const selectedSDG = computed(() => sdgStore.selectedGoal); // Dynamically selected SDG
const shapHighlightedAbstract = ref<string | null>(null);


// Track when the last history check occurred
const lastChecked = ref(new Date());

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

onMounted(async () => {
  await fetchPublicationDetails();

  // TODO: this needs another field to hide it later
  setInterval(async () => {
    await checkLatestWalletUpdate();
  }, 3000);
});

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
    publication_id: publicationId.value,
    voted_label: Number(votedLabel.value),
    abstract_section: markedText.value,
    comment: comment.value,
  };

  try {
    // Submit the annotation first
    const annotationResponse = await $fetch(
      `${config.public.apiUrl}sdg_user_labels/`,
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

    // Emit an event to inform the parent or layout to refetch XP
    emit('xp-updated');

    // Display a toast with the XP gained
    toast.add({
      //title: "XP Gained!",
      title: `You earned ${bankIncrementPayload.increment} XP for your annotation.`,
      type: "success",
      timeout: 5000,
    });

    // Indicate label submission
    labelSubmitted.value = true;

    // Refresh labels and reset fields after submission
    fetchLabels();
    markedText.value = "";
    comment.value = "";
    proposedLabel.value = null;
    votedLabel.value = null;

    // Check for new wallet history entries
    await checkLatestWalletUpdate();

  } catch (err: any) {
    console.error("Submission or scoring failed:", err.message || err);
  }
};

const castVote = async (labelId, voteType, score) => {
  try {
    const payload = {
      user_id: userStore.user?.id, // Get the authenticated user's ID
      sdg_user_label_id: labelId, // The ID of the SDG user label being voted for
      vote_type: voteType, // "upvote", "neutral", or "downvote"
      score: score, // Corresponding score
    };

    // Call the voting API
    const response = await $fetch(`${config.public.apiUrl}votes`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        "Content-Type": "application/json",
      },
      body: payload,
    });

    console.log("Vote submitted successfully:", response);

    // Update the label to reflect that the user has voted
    const updatedLabels = userLabels.value.map((label) => {
      if (label.label_id === labelId) {
        return { ...label, user_voted: true }; // Add a `user_voted` property to disable further voting
      }
      return label;
    });

    userLabels.value = updatedLabels;

    // Optionally, show a success message
    toast.add({
      title: "Vote Recorded",
      type: "success",
      timeout: 3000,
    });
  } catch (err: any) {
    console.error("Failed to cast vote:", err.message || err);
    toast.add({
      title: "Failed to Cast Vote",
      type: "error",
      timeout: 3000,
    });
  }
};

const checkLatestWalletUpdate = async () => {
  try {
    const response = await $fetch(`${config.public.apiUrl}wallets/latest`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });

    // Check if we received a valid history update
    if (response.increment && response.reason) {
      // Show a toast for the latest wallet history entry
      toast.add({
        title: `You earned ${response.increment} coins. Reason: ${response.reason}`,
        type: "success",
        timeout: 5000,
      });
    } else if (response.message) {
      // Handle case where no history updates are available
      console.log("No updates:", response.message);
    } else {
      // Fallback for unexpected response structures
      console.warn("Unexpected response structure:", response);
    }

    // Update the last checked time
    lastChecked.value = new Date();
  } catch (err) {
    console.error("Failed to fetch the latest wallet update:", err.message || err);
    // Optionally, display an error toast
    toast.add({
      title: "Error",
      message: "Failed to fetch wallet updates. Please try again later.",
      type: "error",
      timeout: 5000,
    });
  }
};

// Format dates for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};



const createBarChart = (labelsData) => {
  // Remove existing chart if it exists
  d3.select("#chart-container").selectAll("*").remove();

  const width = 50;
  const height = 50;
  const margin = { top: 20, right: 30, bottom: 50, left: 50 };

  const svg = d3
    .select("#chart-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Prepare the data for the chart
  const labelCounts = d3.rollup(
    labelsData,
    (v) => v.length,
    (d) => d.voted_label
  );

  const data = Array.from(labelCounts, ([label, count]) => ({
    label: `SDG ${label}`,
    count,
    rawLabel: label,
  }));

  // SDG color mapping
  const sdgColors = {
    1: "#E5243B", 2: "#DDA63A", 3: "#4C9F38", 4: "#C5192D", 5: "#FF3A21",
    6: "#26BDE2", 7: "#FCC30B", 8: "#A21942", 9: "#FD6925", 10: "#DD1367",
    11: "#FD9D24", 12: "#BF8B2E", 13: "#3F7E44", 14: "#0A97D9", 15: "#56C02B",
    16: "#00689D", 17: "#19486A"
  };

  // Set up scales
  const x = d3
    .scaleBand()
    .domain(data.map((d) => d.label))
    .range([0, width])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.count)])
    .range([height, 0]);

  // Add axes
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end");

  svg.append("g")
    .call(d3.axisLeft(y).tickValues([])) // Remove ticks
    .select(".domain") // Hide the y-axis line
    .remove();

  // Add bars
  svg
    .selectAll(".bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d) => x(d.label))
    .attr("y", (d) => y(d.count))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.count))
    .attr("fill", (d) => sdgColors[d.rawLabel] || "#CCCCCC"); // Default color if SDG not found

  // Add labels to bars
  svg
    .selectAll(".bar-label")
    .data(data)
    .enter()
    .append("text")
    .attr("class", "bar-label")
    .attr("x", (d) => x(d.label) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.count) - 5)
    .attr("text-anchor", "middle")
    .text((d) => d.count);

  d3.select('#chart-container svg')
    .append("text")
    .attr("class", "chart-title")
    .attr("text-anchor", "middle")
    .attr("x", "50%")
    .attr("y", "5%")
    .style("font-size", "10px")
    .style("font-weight", "bold")
    .text("User Comments Distribution");
};

const createFilteredBarChart = (labelsData) => {
  // Remove existing chart if it exists
  d3.select("#filtered-chart-container").selectAll("*").remove();

  const width = 50;
  const height = 50;
  const margin = { top: 20, right: 30, bottom: 50, left: 50 };

  const svg = d3
    .select("#filtered-chart-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Prepare the data for the chart
  const userVotes = {};
  labelsData.forEach((label) => {
    if (!userVotes[label.user_id]) {
      userVotes[label.user_id] = new Set();
    }
    userVotes[label.user_id].add(label.voted_label);
  });

  const filteredVotes = [];
  Object.values(userVotes).forEach((votes) => {
    votes.forEach((votedLabel) => {
      filteredVotes.push(votedLabel);
    });
  });

  const voteCounts = d3.rollup(
    filteredVotes,
    (v) => v.length,
    (d) => d
  );

  const data = Array.from(voteCounts, ([label, count]) => ({
    label: `SDG ${label}`,
    count,
    rawLabel: label,
  }));

  // SDG color mapping
  const sdgColors = {
    1: "#E5243B", 2: "#DDA63A", 3: "#4C9F38", 4: "#C5192D", 5: "#FF3A21",
    6: "#26BDE2", 7: "#FCC30B", 8: "#A21942", 9: "#FD6925", 10: "#DD1367",
    11: "#FD9D24", 12: "#BF8B2E", 13: "#3F7E44", 14: "#0A97D9", 15: "#56C02B",
    16: "#00689D", 17: "#19486A"
  };

  // Set up scales
  const x = d3
    .scaleBand()
    .domain(data.map((d) => d.label))
    .range([0, width])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.count)])
    .range([height, 0]);

  // Add axes
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end");

  svg.append("g")
    .call(d3.axisLeft(y).tickValues([])) // Remove ticks
    .select(".domain") // Hide the y-axis line
    .remove();

  // Add bars
  svg
    .selectAll(".bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d) => x(d.label))
    .attr("y", (d) => y(d.count))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.count))
    .attr("fill", (d) => sdgColors[d.rawLabel] || "#CCCCCC"); // Default color if SDG not found

  // Add labels to bars
  svg
    .selectAll(".bar-label")
    .data(data)
    .enter()
    .append("text")
    .attr("class", "bar-label")
    .attr("x", (d) => x(d.label) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.count) - 5)
    .attr("text-anchor", "middle")
    .text((d) => d.count);

  d3.select('#filtered-chart-container svg')
    .append("text")
    .attr("class", "chart-title")
    .attr("text-anchor", "middle")
    .attr("x", "50%")
    .attr("y", "5%")
    .style("font-size", "10px")
    .style("font-weight", "bold")
    .text("SDG User Voting");
};



definePageMeta({
  layout: 'user'
})
const calculateVotes = (label, voteType) => {
  // Filter votes for the specific type (positive, neutral, negative) and return the count
  return label.votes?.filter((vote) => vote.vote_type === voteType).length || 0;
};

const calculateScore = (label) => {
  // Sum the scores of all votes for the label
  return label.votes?.reduce((sum, vote) => sum + vote.score, 0) || 0;
};

const toast = useToast()

</script>

<style scoped>
.highlight {
  font-weight: bold;
  padding: 0;
}
</style>
