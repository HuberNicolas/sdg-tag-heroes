<template>
  <div class="min-h-screen flex items-center justify-center p-6">
    <div class="bg-surface/80 backdrop-blur-xl border border-line p-8 rounded-[18px] shadow-panel w-full max-w-md">
      <p class="kicker">// login</p>
      <h2 class="mt-1 text-2xl font-bold tracking-tight mb-6">Login</h2>
      <form @submit.prevent="handleLogin"> <!-- Add @submit.prevent here -->
        <div class="mb-4">
          <label for="email" class="block font-mono text-xs text-fg-dim">email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            class="mt-1.5 block w-full px-3.5 py-2.5 border border-line bg-surface-2 rounded-[10px] transition focus:outline-none focus:ring-4 focus:ring-accent/15 focus:border-accent/60"
          >
        </div>
        <div class="mb-6">
          <label for="password" class="block font-mono text-xs text-fg-dim">password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="mt-1.5 block w-full px-3.5 py-2.5 border border-line bg-surface-2 rounded-[10px] transition focus:outline-none focus:ring-4 focus:ring-accent/15 focus:border-accent/60"
          >
        </div>
        <button
          type="submit"
          class="w-full rounded-[10px] bg-accent py-2.5 px-4 font-mono text-sm font-medium text-surface transition hover:-translate-y-0.5 hover:shadow-glow focus:outline-none focus:ring-4 focus:ring-accent/25"
        >
          Login
        </button>
      </form>
      <div v-if="error" class="mt-4 font-mono text-sm text-hero-red text-center">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No navigation bar before login: it would call the API without a token
import { useAuthentication } from "#imports";

definePageMeta({
  layout: 'none'
})

const email = ref('');
const password = ref('');
const error = ref('');

const auth = useAuthentication();
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  try {
    await auth.login({ email: email.value, password: password.value });
    const profile = await auth.getProfile();
    authStore.setUserProfile(profile);
    router.push('/profile');
  } catch {
    error.value = 'Invalid email or password';
  }
};
</script>
