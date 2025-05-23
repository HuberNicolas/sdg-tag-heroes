<template>
  <div class="relative group w-12 h-12 flex items-center justify-center">
    <!-- Outer container to prevent misalignment due to rotation -->
    <div class="absolute inset-0 flex items-center justify-center">
      <div class="w-12 h-12 bg-primary-500 transform rotate-45 flex items-center justify-center">
        <div class="relative flex items-center justify-center w-10 h-10 bg-white rounded-full">
          <Icon :name="icon" class="w-6 h-6 text-gray-700 transform -rotate-45" />
        </div>
      </div>
    </div>

    <span
      v-if="tooltip"
      class="absolute right-full top-1/2 transform -translate-y-1/2 mr-2 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover:opacity-100 transition-opacity"
    >
      {{ tooltip }}
    </span>
  </div>
</template>



<script setup lang="ts">
defineProps({
  icon: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  tooltip: {
    type: String,
    required: false
  }
});
</script>
