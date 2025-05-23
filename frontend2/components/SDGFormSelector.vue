<template>
  <!-- SDG Selection -->
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">Select SDG</label>
    <select
      v-model="selectedSDG"
      class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
    >
      <option v-for="sdg in sdgs" :key="sdg" :value="sdg">SDG {{ sdg }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">

</script>
