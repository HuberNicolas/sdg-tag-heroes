<template>
  <div class="flex items-center gap-2">
    <UCheckbox
      id="showFinalRound"
      v-model="store.showFinalRound"
      color="primary"
    />
    <label for="showFinalRound" class="text-sm font-medium">
      Count only each person's latest vote
    </label>
  </div>
</template>

<script setup lang="ts">
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";

// Access Pinia store
const store = useLabelDecisionsStore();
</script>
