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
        <li v-for="user in users" :key="user.user_id" class="user-item">
          <router-link :to="`/users/${user.user_id}`" class="user-link">
            <div class="user-avatar">
              <!-- Generate and display the avatar -->
              <UAvatar
                chip-color="primary"
                chip-text=""
                chip-position="top-right"
                size="sm"
                :src="generateUserAvatar(user.email)"
                alt="Avatar"
              />
            </div>
            <div class="user-details">
              <p>
                <strong>{{ user.email }}</strong>
                <span v-if="user.roles.length > 0"> - Roles: {{ user.roles.join(", ") }}</span>
              </p>
              <p>Status: <span :class="{ active: user.is_active, inactive: !user.is_active }">
                {{ user.is_active ? "Active" : "Inactive" }}
              </span></p>
            </div>
          </router-link>
        </li>
      </ul>
      <p v-else>No users found.</p>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted } from "vue";
import UseUser from "@/composables/useUser";
import useAvatar from "@/composables/useAvatar";

// State variables
const users = ref([]);
const loading = ref(true);
const error = ref<string | null>(null);

// Import useAvatar composable
const { generateAvatar } = useAvatar();

// Function to generate avatars based on email
const generateUserAvatar = (email: string) => {
  return generateAvatar({ seed: email, size: 64 }).toDataUri();
};

// Navigate to user details
const goToUser = (userId: string) => {
  router.push(`/users/${userId}`);
};

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

.user-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.user-avatar {
  margin-right: 10px;
}

.user-details p {
  margin: 0;
}

.active {
  color: green;
}

.inactive {
  color: red;
}
</style>
