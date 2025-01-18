<template>
  <table class="table-auto">
    <thead>
    <tr>
      <th>Title</th>
      <th>Glyph</th>
      <th>XP</th>
      <th>Coins</th>
      <th>Top SDG</th>
      <th>Year</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="(item, index) in data" :key="index">
      <td>{{ item.title }}</td>
      <td class="glyph-cell">
        <HexGlyph  :values=item.values :height="100" :width="80" />
      </td>
      <td>{{ item.xp }}</td>
      <td>{{ item.coins }}</td>
      <td>{{ item.topSdg }}</td>
      <td>{{ item.year }}</td>
    </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import HexGlyph from '@/components/PredictionGlyph.vue';

const data = [
  {
    title: 'Example 1',
    values: [0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 0.8, 0.6, 0.4, 0.2, 0.1, 0.3, 0.5],
    xp: 100,
    coins: 50,
    topSdg: 'SDG 5',
    year: 2023,
  },
  {
    title: 'Example 2',
    values: [0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 0.8, 0.6, 0.4, 0.2, 0.1, 0.3, 0.5],
    xp: 100,
    coins: 50,
    topSdg: 'SDG 5',
    year: 2023,
  },
];
</script>

<style>
.table-auto {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
}

th {
  background-color: #f4f4f4;
}

.glyph-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

</style>
