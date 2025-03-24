<template>
  <div>
    <div class="flex flex-col items-center justify-center p-8">Hello World</div>
    <UButton label="Test" />
    <h1>Color mode: {{ $colorMode.value }}</h1>
    <select v-model="$colorMode.preference">
      <option value="system">System</option>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="sepia">Sepia</option>
    </select>
    <UButton
      :icon="isDark ? 'i-heroicons-moon-20-solid' : 'i-heroicons-sun-20-solid'"
      color="gray"
      variant="ghost"
      aria-label="Theme"
      @click="isDark = !isDark"
    />
    <div class="jetbrains-font">Jetbrains Mono</div>
    <div class="press-start-font">Press Start 2P</div>
  </div>
</template>

<script setup lang="ts">
const colorMode = useColorMode();

const isDark = computed({
  get() {
    return colorMode.value === "dark";
  },
  set() {
    colorMode.preference = colorMode.value === "dark" ? "light" : "dark";
  },
});
</script>

<style scoped>
.jetbrains-font {
  font-family: "JetBrains Mono", monospace;
}
.press-start-font {
  font-family: "Press Start 2P", monospace;
}
</style>
