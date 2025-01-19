<template>
  <UTooltip :text="tooltip" :popper="{ arrow: true }">
    <UChip size="3xl" :text="chipText">
      <UButton
        size="xl"
        color="primary"
        variant="solid"
        @click="handleClick(mode)"
        :icon="icon"
      >
      </UButton>
    </UChip>
  </UTooltip>
</template>

<script setup lang="ts">
const props = defineProps({
  mode: {
    type: String,
    required: true,
  },
});

// Lookup for mode details
const modeDetails = {
  '1': {
    icon: 'i-heroicons-scale',
    name: 'Tiebreaker',
    tooltip: 'Resolve conflicts with a balanced approach',
    chipText: '4',
  },
  '2': {
    icon: 'i-heroicons-magnifying-glass',
    name: 'Investigate',
    tooltip: 'Analyze and investigate data',
    chipText: '3',
  },
  '3': {
    icon: 'i-heroicons-map',
    name: 'Search/Explore',
    tooltip: 'Search, explore, or chart new areas',
    chipText: '2',
  },
  '4': {
    icon: 'i-heroicons-check-badge',
    name: 'Confirm the King',
    tooltip: 'Crown the most prominent instance',
    chipText: '1',
  },
  '5': {
    icon: 'i-heroicons-light-bulb',
    name: 'Label Sparse Instances',
    tooltip: 'Label an instance with the least annotations',
    chipText: '3',
  },
};


// Fallback values if mode is not defined in modeDetails
const icon = modeDetails[props.mode]?.icon || 'i-heroicons-question-mark-circle';
const tooltip = modeDetails[props.mode]?.tooltip || 'No details available';
const chipText = modeDetails[props.mode]?.chipText || 'Unknown';

function handleClick(action: string) {
  console.log(action);
}
</script>

<style scoped>
</style>
