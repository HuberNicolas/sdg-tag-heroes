<template>
  <UTooltip :text="'Tooltip'" :popper="{ arrow: true }">
    <UButton
      class="flex flex-col items-center justify-center w-12 h-12 bg-gray-200 rounded-full shadow-md hover:bg-gray-300 focus:outline-none"
      @click="handleClick(props.mode)"
    >
      <component
        :is="AlConfirm"
        class="w-4 h-4"
        :fontControlled="false"
      />
      <UChip :text="'Test'" size="3xl" class="mt-2" />
      <p class="text-sm mt-2 text-gray-600">{{ props.name }}</p>
    </UButton>
  </UTooltip>
</template>

<script setup lang="ts">

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  mode: {
    type: String,
    required: true,
  }
});


import AlConfirm from '~/assets/al_confirm.svg?component';
import AlExplore from '~/assets/al_explore.svg?component';
import AlInvestigate from '~/assets/al_investigate.svg?component';
import AlTiebreaker from '~/assets/al_tiebreaker.svg?component';
import AlLeastLabeled from '~/assets/al_least_labeled.svg?component';


function handleClick(action: string) {
  console.log(action);
}


</script>

<style>

</style>
