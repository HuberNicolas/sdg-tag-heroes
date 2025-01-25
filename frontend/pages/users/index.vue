<template>
  <div class="p-5">
    <h1 class="text-2xl font-bold mb-6">User List</h1>

    <!-- Loading State -->
    <div v-if="loading" class="text-blue-500 text-lg">
      Loading users...
    </div>

    <!-- Error State -->
    <div v-if="error" class="text-red-500 text-lg">
      <p>An error occurred: {{ error }}</p>
    </div>

    <!-- User List -->
    <div v-else>
      <ul v-if="users.length > 0" class="space-y-4">
        <li
          v-for="user in users"
          :key="user.user_id"
          class="flex items-center p-4 border border-gray-300 rounded-lg shadow-sm hover:shadow-md transition-shadow"
        >
          <router-link :to="`/users/${user.user_id}`" class="flex items-center w-full">
            <!-- Avatar -->
            <div class="mr-4">
              <img
                :src="generateAvatar(user.email)"
                alt="User Avatar"
                class="w-12 h-12 rounded-full"
              />
            </div>

            <!-- User Details -->
            <div class="flex-grow">
              <p class="font-semibold text-lg">
                {{ user.email }}
                <span v-if="user.roles.length > 0" class="text-sm text-gray-600 ml-1">
                  - Roles: {{ user.roles.join(", ") }}
                </span>
              </p>
              <p class="text-sm">
                Status:
                <span
                  :class="{
                    'text-green-500 font-semibold': user.is_active,
                    'text-red-500 font-semibold': !user.is_active
                  }"
                >
                  {{ user.is_active ? "Active" : "Inactive" }}
                </span>
              </p>
            </div>
          </router-link>
        </li>
      </ul>

      <!-- No Users Found -->
      <p v-else class="text-gray-600 text-center text-lg">No users found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useUsersStore } from "~/stores/users";
import { generateAvatar } from "~/utils/avatar";

// Reactive State
const loading = ref(true);
const error = ref<string | null>(null);

// Use the user store
const userStore = useUsersStore();
const users = ref([]);

// Fetch users on component mount
onMounted(async () => {
  try {
    await userStore.fetchUsers(); // Fetch users using the store
    users.value = userStore.users; // Populate the local state with users
  } catch (err) {
    console.error("Error fetching users:", err);
    error.value = err.message || "Failed to load users.";
  } finally {
    loading.value = false;
  }
});
</script>
