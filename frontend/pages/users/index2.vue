<template>
  <div class="p-5 font-sans">
    <h1 class="text-2xl font-bold mb-4">User List</h1>

    <!-- Display a loading state -->
    <div v-if="loading" class="text-blue-500">
      Loading users...
    </div>

    <!-- Display an error state -->
    <div v-if="error" class="text-red-500">
      <p>An error occurred: {{ error }}</p>
    </div>

    <!-- Display the list of users -->
    <div v-else>
      <ul v-if="users.length > 0" class="space-y-4">
        <li v-for="user in users" :key="user.userId" class="flex items-center p-4 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
          <router-link :to="`/users/${user.userId}`" class="flex items-center w-full">
            <!-- User Avatar -->
            <div class="mr-4">
              <div v-if="!avatarLoaded[user.userId]" class="w-12 h-12 rounded-full bg-gray-200 animate-pulse"></div>
              <img
                v-else
                :src="generateAvatar(user.email)"
                :alt="`Avatar for ${user.email}`"
                class="w-12 h-12 rounded-full"
                @load="handleAvatarLoad(user.userId)"
              />
            </div>

            <!-- User Details -->
            <div class="flex-grow">
              <p class="font-semibold">
                {{ user.email }}
                <span v-if="user.roles.length > 0" class="text-gray-600"> - Roles: {{ user.roles.join(", ") }}</span>
              </p>
              <p class="text-sm">
                Status:
                <span :class="{ 'text-green-500': user.isActive, 'text-red-500': !user.isActive }">
                  {{ user.isActive ? "Active" : "Inactive" }}
                </span>
              </p>
            </div>
          </router-link>
        </li>
      </ul>
      <p v-else class="text-gray-600">No users found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useUsersStore } from "~/stores/users";
import { generateAvatar } from "~/utils/avatar"; // Import the utility function

// State variables
const users = ref([]);
const loading = ref(true);
const error = ref<string | null>(null);
const avatarLoaded = ref<Record<number, boolean>>({}); // Track avatar loading state

// Use the user store
const userStore = useUsersStore();

// Function to handle avatar load
const handleAvatarLoad = (userId: number) => {
  console.log('Avatar loaded for user ID:', userId); // Debugging
  avatarLoaded.value[userId] = true; // Mark avatar as loaded
};

// Fetch users on mount
onMounted(async () => {
  try {
    await userStore.fetchUsers(); // Fetch users from the API
    users.value = userStore.users;

    // Initialize avatar loading state
    users.value.forEach((user) => {
      avatarLoaded.value[user.userId] = false; // Use user.userId as the key
    });

    console.log('Users fetched:', users.value); // Debugging
    console.log('Avatar loaded state initialized:', avatarLoaded.value); // Debugging
  } catch (err) {
    console.error("Error fetching users:", err);
    error.value = err.message || "Failed to load users.";
  } finally {
    loading.value = false; // Set loading to false after fetch
  }
});
</script>
