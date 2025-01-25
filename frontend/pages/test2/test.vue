<script setup lang="ts">
import { useSDGPredictionsStore } from "~/stores/sdgPredictions";
import { onMounted } from "vue";

// Initialize the SDG Predictions store
const sdgPredictionsStore = useSDGPredictionsStore();

// Fetch SDG predictions on component mount
onMounted(async () => {
  const publicationIds = [1, 2, 3];
  await sdgPredictionsStore.fetchSDGPredictionsByPublicationIds(publicationIds);
});

// Access state
const sdgPredictions = computed(() => sdgPredictionsStore.sdgPredictions);
const isLoading = computed(() => sdgPredictionsStore.isLoading);
const error = computed(() => sdgPredictionsStore.error);
</script>

<template>
  <div>
    <h1>SDG Predictions</h1>
    <p v-if="isLoading">Loading...</p>
    <p v-else-if="error">{{ error }}</p>
    <ul v-else>
      <li v-for="prediction in sdgPredictions" :key="prediction.predictionId">
        <h2>Prediction ID: {{ prediction.predictionId }}</h2>
        <p>Publication ID: {{ prediction.publicationId }}</p>
        <p>Prediction Model: {{ prediction.predictionModel }}</p>
        <p>Predicted: {{ prediction.predicted ? "Yes" : "No" }}</p>
        <p>Last Predicted Goal: {{ prediction.lastPredictedGoal }}</p>
        <h3>SDG Scores:</h3>
        <ul>
          <li v-for="(score, index) in prediction.sdgScores" :key="index">
            SDG {{ index + 1 }}: {{ score }}
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>
