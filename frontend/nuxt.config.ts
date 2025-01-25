// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-04-03",
  devtools: {
    enabled: true,
    timeline: {
      enabled: true
    }
  },
  ssr: false,
  modules: [
    "@nuxt/fonts",
    "@nuxt/ui",
    "@nuxtjs/color-mode",
    "@nuxt/eslint",
    "@nuxt/content",
    "nuxt-svgo",
    "@nuxt/image",
    '@pinia/nuxt'
  ],
  imports: {
    // https://nuxt.com/docs/guide/directory-structure/composables
    dirs: [
      // scan all modules within given directory
      'composables/**'
    ]
  },
  vite: {
    server: {
      // https://github.com/vitejs/vite/issues/15784
      watch: {
        usePolling: true,
      },
      hmr: {
        clientPort: 3030 // Host's port
      }
    }
  },
  content: {
    // https://content.nuxt.com/get-started/configuration#watch
    watch: false
  },
  runtimeConfig: {
    public: {
      apiUrl: process.env.API_URL // FastAPI, verifies jwt
    }
  },
  // add the middleware globally by adding
  router: {
    middleware: ["authentication"]
  },
  ui: {
    icons: ["mdi", "simple-icons"]
  },
  // clear local storage after changing this
  colorMode: {
    preference: "system", // default value of $colorMode.preference
    fallback: "light", // fallback value if not system preference found
    hid: "nuxt-color-mode-script",
    globalName: "__NUXT_COLOR_MODE__",
    componentName: "ColorScheme",
    classPrefix: "",
    classSuffix: "-mode",
    storage: "localStorage", // or 'sessionStorage' or 'cookie'
    storageKey: "nuxt-color-mode"
  },
  fonts: {
    families: [
      {
        name: "JetBrains Mono",
        provider: "google",
        fallbacks: ["Times New Roman"]
      },
      {
        name: "Press Start 2P",
        provider: "google",
        fallbacks: ["Times New Roman"]
      }
    ],
    defaults: {
      fallbacks: {
        monospace: ["Tahoma"]
      }
    }
  },
  watch: ['composables/**/*.ts', 'components/**/*.vue'], // does not trigger new build
});
