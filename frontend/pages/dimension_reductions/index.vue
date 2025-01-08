<template>
  <div class="container">
    <h1>Dimensionality Reductions Query</h1>

    <form @submit.prevent="fetchData">
      <div class="form-group">
        <label for="sdg">SDGs (comma-separated)</label>
        <input
          id="sdg"
          v-model="formData.sdg"
          type="text"
          placeholder="e.g., 1,4,12"
        />
      </div>

      <div class="form-group">
        <label for="level">Levels (comma-separated)</label>
        <input
          id="level"
          v-model="formData.level"
          type="text"
          placeholder="e.g., 1,2,3"
        />
      </div>

      <div class="form-group">
        <label for="reduction-shorthand">Reduction Shorthand</label>
        <input
          id="reduction-shorthand"
          v-model="formData.reduction_shorthand"
          type="text"
          placeholder="e.g., UMAP-15-0.1-2"
        />
      </div>

      <div class="form-group">
        <label for="limit">Limit</label>
        <input
          id="limit"
          v-model.number="formData.limit"
          type="number"
          placeholder="e.g., 10"
        />
      </div>

      <button type="submit" class="btn btn-primary">Fetch Reductions</button>
    </form>

    <div v-if="error" class="alert alert-danger mt-4">
      {{ error }}
    </div>

    <div v-if="isFetching || pending" class="mt-4">
      <p>Loading...</p>
    </div>

    <div v-if="reductions && Object.keys(reductions.reductions).length" class="reductions-list mt-4">
      <h2>Results</h2>
      <div v-for="(levels, sdg) in reductions.reductions" :key="sdg" class="sdg-group">
        <h3>SDG {{ sdg.replace('sdg', '') }}</h3>
        <div v-for="(reductionList, level) in levels" :key="level" class="level-group">
          <h4>Level {{ level.replace('level', '') }}</h4>
          <ul>
            <li v-for="reduction in reductionList" :key="reduction.dim_red_id">
              <p><strong>ID:</strong> {{ reduction.dim_red_id }}</p>
              <p><strong>Technique:</strong> {{ reduction.reduction_technique }}</p>
              <p><strong>Coords:</strong> ({{ reduction.x_coord }}, {{ reduction.y_coord }}, {{ reduction.z_coord }})</p>
              <p><strong>Shorthand:</strong> {{ reduction.reduction_shorthand }}</p>
              <p><strong>Created At:</strong> {{ new Date(reduction.created_at).toLocaleDateString() }}</p>
              <p><strong>Updated At:</strong> {{ new Date(reduction.updated_at).toLocaleDateString() }}</p>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div v-else-if="reductions && !Object.keys(reductions.reductions).length" class="mt-4">
      <p>No results found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRuntimeConfig } from "nuxt/app";

const config = useRuntimeConfig();


import type { DimensionalityReductionResponse } from '~/types/dimensionalityReduction'

// Default query parameters
const defaultSdgs = Array.from({ length: 17 }, (_, i) => i + 1)
const defaultLevels = Array.from({ length: 3 }, (_, i) => i + 1)
const defaultLimit = 1

const formData = ref({
  sdg: defaultSdgs.join(','),
  level: defaultLevels.join(','),
  reduction_shorthand: '',
  limit: defaultLimit,
})

// Fetch initial data using useAsyncData
const { data: reductions, pending, error } = useAsyncData<DimensionalityReductionResponse>(
  'dimensionality-reductions',
  () =>

    $fetch(`${config.public.apiUrl}dimensionality_reductions`, {
      method: 'GET',
      params: {
        sdg: defaultSdgs,
        level: defaultLevels,
        limit: defaultLimit,
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
)

const isFetching = ref(false)

const fetchData = async () => {
  isFetching.value = true
  error.value = null

  try {
    const sdgQuery = formData.value.sdg.split(',').map(Number)
    const levelQuery = formData.value.level.split(',').map(Number)

    const response = await $fetch<DimensionalityReductionResponse>(`${config.public.apiUrl}dimensionality_reductions`, {
      method: 'GET',
      params: {
        sdg: sdgQuery,
        level: levelQuery,
        reduction_shorthand: formData.value.reduction_shorthand,
        limit: formData.value.limit,
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })

    reductions.value = response
  } catch (err) {
    error.value = err.message || 'An error occurred while fetching data.'
  } finally {
    isFetching.value = false
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
.btn {
  margin-top: 10px;
}
.reductions-list {
  border-top: 1px solid #ddd;
  padding-top: 20px;
}
.sdg-group {
  margin-top: 20px;
}
.level-group {
  margin-left: 20px;
}
</style>
