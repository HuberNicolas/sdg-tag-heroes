<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="email">Email:</label>
        <input v-model="email" type="email" id="email" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input v-model="password" type="password" id="password" required />
      </div>
      <UButton type="submit">Login</UButton>
    </form>
    <div v-if="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import useAuthentication from '~/composables/useAuthentication';

const email = ref('');
const password = ref('');
const error = ref('');
const router = useRouter();

const handleLogin = async () => {
  try {
    const authService = useAuthentication(); // Call as a function
    await authService.login({ email: email.value, password: password.value });
    await router.push('/profile'); // Navigate to profile page after login
  } catch (err) {
    error.value = 'Invalid email or password';
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
}
</style>
