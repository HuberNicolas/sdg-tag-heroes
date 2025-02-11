<template>
  <div class="min-h-screen bg-black flex flex-col justify-center items-center text-white">
    <NuxtParticles
      id="tsparticles"
      :options="options"
      @load="onLoad"
      class="absolute inset-0, z-0"
    ></NuxtParticles>

    <!-- Title Section -->
    <div class="text-5xl font-extrabold text-center mb-8 press-start-font z-10">
      SDG Tag Heroes
    </div>

    <!-- Dynamic Text Section -->
    <ClientOnly>
      <VueWriter
        :array="[
          'Exploring Gamification to Enhance SDG Labeling',
          'Join the Global Effort to Achieve SDGs!',
          'A New Approach to Labeling with Citizen Science',
          'Your Contribution Makes a Global Impact!',
          'Gamified Labeling: Fun and Effective!'
        ]"
        :typeSpeed="70"
        :eraseSpeed="50"
        :delay="1000"
        class="text-xl md:text-2xl font-medium text-center z-10"
      />
    </ClientOnly>

    <!-- Main Content Section -->
    <div class="mt-12 p-8 bg-black rounded-lg shadow-lg w-full max-w-3xl z-10">
      <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>
      <form @submit.prevent="handleLogin">
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
import type { Container } from '@tsparticles/engine';
import { baseSdgColors } from "@/constants/constants";
import { VueWriter } from 'vue-writer';

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
  } catch (err) {
    error.value = 'Invalid email or password';
  }
};

const options = {
  "particles": {
    "number": {
      "value": 100,
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
        "width": 1,
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
      "color": "#ffffff",
      "opacity": 0.6,  // Increased opacity for more visible connections
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
  layout: 'empty'
})

</script>

<style scoped>
.press-start-font {
  font-family: "Press Start 2P", monospace;
}
</style>
