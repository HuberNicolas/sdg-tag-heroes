<template>
  <div class="flex items-center gap-2">
    <UCheckbox
      id="showAllSDGUserLabels"
      v-model="store.showAllSDGUserLabels"
      color="primary"
      size="sm"
    />
    <label for="showAllSDGUserLabels" class="text-sm font-medium">
      Include All User Votes
    </label>
  </div>
</template>

<script setup lang="ts">
import { useLabelDecisionsStore } from "~/stores/sdgLabelDecisions";

// Access Pinia store
const store = useLabelDecisionsStore();
</script>
