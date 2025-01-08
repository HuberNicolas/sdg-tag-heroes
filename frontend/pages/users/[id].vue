<template>
  <div class="user-details-page">
    <h1>User Details</h1>

    <div v-if="loading" class="loading">Loading user details...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="user && !loading" class="user-details">
      <div class="user-avatar">
        <UAvatar
          chip-color="primary"
          chip-text=""
          chip-position="top-right"
          size="lg"
          :src="generateUserAvatar(user.email)"
          alt="Avatar"
        />
      </div>
      <div class="user-info">
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Roles:</strong> {{ user.roles.join(", ") || "None" }}</p>
        <p><strong>Status:</strong> {{ user.is_active ? "Active" : "Inactive" }}</p>
      </div>
      <UButton label="Back to Users" @click="goBack" />
    </div>
  </div>
</template>

<script setup lang="ts">
import useAvatar from "@/composables/useAvatar";
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import UseUser from "@/composables/useUser";


// State
const user = ref(null);
const loading = ref(true);
const error = ref<string | null>(null);

// Routing
const router = useRouter();
const route = useRoute();
const userId = Number(route.params.id);

// Avatar generation
const { generateAvatar } = useAvatar();
const generateUserAvatar = (email: string) => {
  return generateAvatar({ seed: email, size: 128 }).toDataUri();
};

// Fetch user details
onMounted(async () => {
  const useUser = new UseUser();
  try {
     // Fetch single user by ID
    user.value = await useUser.getUserById(userId); // Assuming the API returns a single user object
  } catch (err) {
    console.error("Error fetching user:", err);
    error.value = err.message || "Failed to load user details.";
  } finally {
    loading.value = false;
  }
});

// Go back to the user list
const goBack = () => {
  router.push("/users");
};
</script>

<style scoped>
.user-details-page {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.loading {
  color: #007bff;
}

.error {
  color: red;
}

.user-details {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  flex-shrink: 0;
}

.user-info p {
  margin: 5px 0;
}
</style>
