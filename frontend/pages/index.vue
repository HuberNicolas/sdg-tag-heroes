<template>
  <div class="landing relative min-h-screen overflow-hidden">
    <NuxtParticles
      id="tsparticles"
      :options="options"
      class="absolute inset-0 z-0 opacity-60 dark:opacity-80"
      @load="onLoad"
    />

    <!-- Top bar -->
    <header class="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
      <span class="flex items-center gap-2.5 font-mono text-sm text-fg-dim">
        <span class="grid h-8 w-8 place-items-center rounded-[10px] border border-line bg-surface/70 text-accent">
          <svg viewBox="0 0 32 32" fill="none" class="h-5 w-5" aria-hidden="true">
            <path d="M16 3.5 26.8 9.75v12.5L16 28.5 5.2 22.25V9.75Z" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />
            <path d="M16 10.5 20.8 13.25v5.5L16 21.5l-4.8-2.75v-5.5Z" fill="currentColor" />
          </svg>
        </span>
        <span>sdg<span class="text-accent">.</span>tag<span class="text-accent">.</span>heroes</span>
      </span>
      <button
        type="button"
        class="grid h-9 w-9 place-items-center rounded-full border border-line bg-surface/70 text-fg-dim backdrop-blur transition-colors hover:text-fg"
        :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        @click="toggleColorMode"
      >
        <Icon :name="isDark ? 'line-md:sunny-outline' : 'line-md:moon'" class="h-[18px] w-[18px]" />
      </button>
    </header>

    <main class="relative z-10 mx-auto grid max-w-6xl items-center gap-12 px-6 pb-16 pt-6 lg:min-h-[calc(100vh-84px)] lg:grid-cols-[1.15fr_1fr] lg:pt-0">
      <!-- Hero -->
      <section class="animate-fade-up">
        <p class="kicker mb-5">// gamified citizen science for the UN SDGs</p>

        <!-- Title Section -->
        <h1 class="pixel gradient-text text-[28px] leading-[1.35] sm:text-4xl lg:text-[44px]">
          SDG Tag<br>Heroes
        </h1>

        <!-- Dynamic Text Section -->
        <div class="mt-6 flex min-h-[2em] items-baseline gap-2 font-mono text-base text-fg-dim sm:text-lg">
          <span class="text-accent">&gt;</span>
          <ClientOnly>
            <VueWriter
              :array="[
                'Which SDGs does this research serve?',
                'Machine predictions, checked by people',
                'Labeling research publications as citizen science',
                'Read, compare, decide',
                'Every label is a data point'
              ]"
              :type-speed="70"
              :erase-speed="50"
              :delay="1000"
              class="writer"
            />
          </ClientOnly>
        </div>

        <p class="mt-6 max-w-xl text-fg-dim">
          Machine-learning models estimate which of the 17 Sustainable Development Goals a research publication relates
          to, and they are often unsure. Here you read the abstracts, look at what the model based its estimate on, compare
          it with the votes of others and decide. Your labels show where the models are right and where they are not.
        </p>

        <div class="mt-8 flex flex-wrap gap-2">
          <span v-for="step in steps" :key="step.label" class="stat-pill">
            <Icon :name="step.icon" class="h-3.5 w-3.5 text-accent" />{{ step.label }}
          </span>
        </div>
      </section>

      <!-- Main Content Section -->
      <section class="animate-fade-up [animation-delay:120ms]">
        <div class="relative">
          <HoneycombMark class="absolute -right-8 -top-28 hidden w-40 lg:block" :labels="false" />

          <div class="login-card relative">
            <p class="kicker">// login</p>
            <h2 class="mt-1 text-2xl font-bold tracking-tight">Log in</h2>
            <p class="mt-1 text-sm text-fg-dim">Continue where you left off.</p>

            <form class="mt-6 space-y-4" @submit.prevent="handleLogin">
              <div>
                <label for="email" class="field-label">email</label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  required
                  autocomplete="username"
                  placeholder="hero@example.org"
                  class="field-input"
                >
              </div>
              <div>
                <label for="password" class="field-label">password</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  required
                  autocomplete="current-password"
                  placeholder="••••••••"
                  class="field-input"
                >
              </div>
              <button type="submit" class="login-btn group">
                Login
                <Icon name="mdi-arrow-right" class="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </button>
            </form>
            <div v-if="error" class="mt-4 flex items-center gap-2 rounded-lg border border-hero-red/30 bg-hero-red/10 px-3 py-2 font-mono text-sm text-hero-red">
              <Icon name="mdi-alert-hexagon-outline" class="h-4 w-4 flex-none" />{{ error }}
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="relative z-10 mx-auto max-w-6xl px-6 pb-6 font-mono text-xs text-fg-faint">
      master's thesis · university of zurich
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useAuthentication } from "#imports";
import type { Container } from '@tsparticles/engine';
import { baseSdgColors } from "@/constants/constants";
import { VueWriter } from 'vue-writer';

const email = ref('');
const password = ref('');
const error = ref('');

const steps = [
  { icon: 'mdi-map-search-outline', label: 'explore' },
  { icon: 'mdi-tag-outline', label: 'label' },
  { icon: 'mdi-vote-outline', label: 'vote' },
  { icon: 'mdi-trophy-outline', label: 'level up' },
];

// Light / dark theme switch
const colorMode = useColorMode();
const isDark = computed(() => colorMode.value === 'dark');
const toggleColorMode = () => {
  colorMode.preference = isDark.value ? 'light' : 'dark';
};

const auth = useAuthentication();
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  try {
    await auth.login({ email: email.value, password: password.value });
    const profile = await auth.getProfile();
    authStore.setUserProfile(profile);
    router.push('/scenarios');
  } catch {
    error.value = 'Invalid email or password';
  }
};

const options = {
  // Behind the page content
  "fullScreen": {
    "enable": true,
    "zIndex": -1
  },
  "particles": {
    "number": {
      "value": 70,
      "density": {
        "enable": true,
        "value_area": 800
      }
    },
    "color": {
      "value": baseSdgColors
    },
    "shape": {
      "type": "polygon",
      "sides": 6,
      "stroke": {
        "width": 0,
        "color": "#000000"
      }
    },
    "opacity": {
      "value": 0.5,
      "random": false,
      "anim": {
        "enable": false,
        "speed": 1,
        "opacity_min": 0.1,
        "sync": false
      }
    },
    "size": {
      "value": 10,
      "random": true,
      "anim": {
        "enable": false,
        "speed": 40,
        "size_min": 0.1,
        "sync": false
      }
    },
    "line_linked": {
      "enable": true,
      "distance": 80,  // Reduced distance for stronger proximity effect
      "color": "#8a8aa0", // readable on the light and the dark background
      "opacity": 0.35,
      "width": 1,
      "conservative": false,
      "frequency": 1,
      "smooth": true,
      "warriors": {
        "enable": true,
        "scoring": "reciprocal"
      }
    },
    "move": {
      "enable": true,
      "speed": 1,
      "direction": "none",
      "random": false,
      "straight": false,
      "out_mode": "out",
      "bounce": false,
      "attract": {
        "enable": true,  // Added attraction between particles
        "rotateX": 3000,
        "rotateY": 3000
      }
    }
  },
  "interactivity": {
    "detect_on": "canvas",
    "events": {
      "onhover": {
        "enable": true,
        "mode": "repulse"
      },
      "onclick": {
        "enable": true,
        "mode": "push"
      },
      "resize": true
    },
    "modes": {
      "grab": {
        "distance": 400,
        "line_linked": {
          "opacity": 1
        }
      },
      "bubble": {
        "distance": 400,
        "size": 40,
        "duration": 2,
        "opacity": 8,
        "speed": 3
      },
      "repulse": {
        "distance": 200,
        "duration": 0.4
      },
      "push": {
        "particles_nb": 4
      },
      "remove": {
        "particles_nb": 2
      }
    }
  },
  "retina_detect": true
}


const onLoad = (container: Container) => {
  // Do something with the container
  container.pause()
  setTimeout(() => container.play(), 2000)
}

definePageMeta({
  layout: 'none'
})

</script>

<style scoped>
.login-card {
  @apply rounded-[18px] border border-line bg-surface/80 p-7 backdrop-blur-xl sm:p-8;
  box-shadow: var(--shadow);
}
.login-card::before {
  /* thin gradient edge on top of the card */
  content: '';
  @apply absolute inset-x-8 top-0 h-px;
  background: linear-gradient(90deg, transparent, rgb(var(--c-accent) / 0.7), rgb(var(--c-blue) / 0.6), transparent);
}

.field-label {
  @apply mb-1.5 block font-mono text-xs text-fg-dim;
}
.field-input {
  @apply block w-full rounded-[10px] border border-line bg-surface-2 px-3.5 py-2.5 text-fg placeholder:text-fg-faint transition;
}
.field-input:focus {
  @apply border-accent/60 outline-none ring-4 ring-accent/15;
}

.login-btn {
  @apply mt-2 inline-flex w-full items-center justify-center gap-2 rounded-[10px] border border-accent/40 px-4 py-3 font-mono text-sm font-medium text-fg transition-all duration-200;
  background: linear-gradient(120deg, rgb(var(--c-accent) / 0.18), rgb(var(--c-blue) / 0.14));
}
.login-btn:hover {
  @apply -translate-y-0.5 border-accent/70 shadow-glow;
}

.writer :deep(.typed-cursor),
.writer :deep(.cursor) {
  @apply bg-accent;
}
</style>
