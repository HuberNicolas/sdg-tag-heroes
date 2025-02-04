<template>
  <div class="flex items-center gap-2">
    <input
      id="showAllSDGUserLabels"
      v-model="store.showAllSDGUserLabels"
      type="checkbox"
      class="h-4 w-4"
    />
    <label for="showAllSDGUserLabels" class="text-sm font-medium">
      Show all SDG User Labels
    </label>
  </div>
</template>

<script setup lang="ts">
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";

// Access Pinia store
const store = useLabelDecisionsStore();
</script>
