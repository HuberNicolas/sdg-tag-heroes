<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>
      <form @submit.prevent="handleLogin"> <!-- Add @submit.prevent here -->
        <div class="mb-4">
          <label for="email" class="block text-sm font-medium text-gray-700">Email:</label>
          <input
            v-model="email"
            type="email"
            id="email"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div class="mb-6">
          <label for="password" class="block text-sm font-medium text-gray-700">Password:</label>
          <input
            v-model="password"
            type="password"
            id="password"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <button
          type="submit"
          class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          Login
        </button>
      </form>
      <div v-if="error" class="mt-4 text-red-600 text-center">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthentication } from "#imports";

const email = ref('');
const password = ref('');
const error = ref('');

const auth = useAuthentication();
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  try {
    const response = await auth.login({ email: email.value, password: password.value });
    const profile = await auth.getProfile();
    authStore.setUserProfile(profile);
    router.push('/profile');
  } catch (err) {
    error.value = 'Invalid email or password';
  }
};
</script>
