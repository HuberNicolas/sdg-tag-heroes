<template>
  <div class="users-page">
    <h1>User List</h1>

    <!-- Display a loading state -->
    <div v-if="loading" class="loading">
      Loading users...
    </div>

    <!-- Display an error state -->
    <div v-if="error" class="error">
      <p>An error occurred: {{ error }}</p>
    </div>

    <!-- Display the list of users -->
    <div v-else>
      <ul v-if="users.length > 0" class="user-list">
        <li v-for="user in users" :key="user.user_id">
          <p>
            <strong>{{ user.email }}</strong>
            <span v-if="user.roles.length > 0"> - Roles: {{ user.roles.join(", ") }}</span>
          </p>
          <p>Status: <span :class="{ active: user.is_active, inactive: !user.is_active }">
            {{ user.is_active ? "Active" : "Inactive" }}
          </span></p>
        </li>
      </ul>
      <p v-else>No users found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import UseUser from "@/composables/useUser";

// State variables
const users = ref([]);
const loading = ref(true);
const error = ref<string | null>(null);

// Fetch users on mount
onMounted(async () => {
  const useUser = new UseUser();
  try {
    const response = await useUser.getUsers(); // Fetch users from the API
    users.value = response.items;
  } catch (err) {
    console.error("Error fetching users:", err);
    error.value = err.message || "Failed to load users.";
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.users-page {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  font-size: 24px;
  margin-bottom: 10px;
}

.loading {
  color: #007bff;
}

.error {
  color: red;
}

.user-list {
  list-style: none;
  padding: 0;
}

.user-list li {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

.user-list li p {
  margin: 5px 0;
}

.active {
  color: green;
}

.inactive {
  color: red;
}
</style>
