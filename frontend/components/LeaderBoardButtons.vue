<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="col-span-2">
      <div class="flex justify-between items-center">
        <!-- Left Section: Four Buttons -->
        <div class="flex space-x-4">
          <UTooltip
            v-for="(icon, index) in leftIcons"
            :key="index"
            :text="icon.tooltip"
            :popper="{ arrow: true }"
          >
            <UButton
              class="flex flex-col items-center justify-center w-72 h-72 bg-gray-200 rounded-full shadow-md hover:bg-gray-300 focus:outline-none"
              @click="handleClick(icon.action)"
            >
              <component
                :is="icon.component"
                class="w-36 h-36"
                :fontControlled="false"
              />
              <UChip :text="icon.value" size="3xl" class="mt-2" />
              <p class="text-sm mt-2 text-gray-600">{{ icon.label }}</p>
            </UButton>
          </UTooltip>
        </div>

        <!-- Right Section: Fifth Button -->
        <UTooltip :text="rightIcon.tooltip" :popper="{ arrow: true }">
          <UButton
            class="flex flex-col items-center justify-center w-72 h-72 bg-gray-200 rounded-full shadow-md hover:bg-gray-300 focus:outline-none"
            @click="handleClick(rightIcon.action)"
          >
            <component
              :is="rightIcon.component"
              class="w-36 h-36"
              :fontControlled="false"
            />
            <UChip :text="rightIcon.value" size="3xl" class="mt-2" />
            <p class="text-sm mt-2 text-gray-600">{{ rightIcon.label }}</p>
          </UButton>
        </UTooltip>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import alConfirm from '~/assets/al_confirm.svg?component';
import alExplore from '~/assets/al_explore.svg?component';
import alInvestigate from '~/assets/al_investigate.svg?component';
import alTiebreaker from '~/assets/al_tiebreaker.svg?component';
import alLeastLabeled from '~/assets/al_least_labeled.svg?component';

const leftIcons = [
  { component: alTiebreaker, action: 'tiebreaker', value: "$$$$", label: "Tiebreaker", tooltip: "This is the Tiebreaker option" },
  { component: alInvestigate, action: 'investigate', value: "$$$", label: "Investigate", tooltip: "This is the Investigate option" },
  { component: alExplore, action: 'explore', value: "$$", label: "Explore", tooltip: "This is the Explore option" },
  { component: alConfirm, action: 'confirm', value: "$", label: "Confirm", tooltip: "This is the Confirm option" },
];

const rightIcon = { component: alLeastLabeled, action: 'least_labeled', value: "$$$", label: "Least Labeled", tooltip: "This is the Least Labeled option" };

const handleClick = (action: string) => {
  console.log(`Button clicked: ${action}`);
  // Add action handling logic here, e.g., navigation or API calls
};
</script>

<style scoped>
button {
  transition: transform 0.2s;
}
button:hover {
  transform: scale(1.1);
}
p {
  text-align: center;
}
</style>
