<script setup lang="ts">
const links = [
  [{
    label: 'Home',
    icon: 'i-heroicons-home',
    to: '/getting-started/installation'
  }, {
    label: 'Horizontal Navigation',
    icon: 'i-heroicons-chart-bar',
    to: '/components/horizontal-navigation'
  }, {
    label: 'Commands',
    icon: 'i-heroicons-command-line',
    to: '/components/command-palette'
  },
    {
      label: 'Publications',
      icon: 'i-heroicons-document-duplicate',
      to: '/publications'
    }], [{
    label: 'Profile',
    icon: 'i-heroicons-light-bulb'
  }, {
    label: 'Help',
    icon: 'i-heroicons-question-mark-circle'
  },
    {
      label: 'Personal',
      icon: 'i-heroicons-user'
    }]
]
</script>

<template>
  <UHorizontalNavigation :links="links" class="border-b border-gray-200 dark:border-gray-800" />
</template>

