<template>
  <div class="flex items-center gap-2">
    <UCheckbox
      id="showFinalRound"
      v-model="store.showFinalRound"
      color="primary"
      size="sm"
    />
    <label for="showFinalRound" class="text-sm font-medium">
      Final Round Vote: Only Last Vote Counts
    </label>
  </div>
</template>

<script setup lang="ts">
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";

// Access Pinia store
const store = useLabelDecisionsStore();
</script>
