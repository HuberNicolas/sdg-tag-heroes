// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: {
    enabled: false,
    timeline: {
      enabled: true
    }
  },
  ssr: false,
  modules: [
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/ui',

    //"@nuxtjs/color-mode",
    "nuxt-svgo",
    '@pinia/nuxt',
    'nuxt-particles'
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
    preference: "light", // default value of $colorMode.preference // system also possible
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
})
