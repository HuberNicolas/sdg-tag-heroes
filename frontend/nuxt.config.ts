// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-04-03",
  devtools: {
    enabled: false,
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
    build: {
      // Plotly alone is a chunk of several MB; it is loaded on purpose
      chunkSizeWarningLimit: 5000
    },
    server: {
      // https://github.com/vitejs/vite/issues/15784
      watch: {
        usePolling: true,
      },
      // In Docker, the browser reaches the dev server through the host port (see docker-compose.yml)
      hmr: process.env.HMR_CLIENT_PORT
        ? { clientPort: Number(process.env.HMR_CLIENT_PORT) }
        : undefined
    }
  },
  runtimeConfig: {
    public: {
      apiUrl: process.env.API_URL, // FastAPI, verifies jwt
      // Parts the overview map is split into (one per universe); use a small number for small datasets.
      // Override with NUXT_PUBLIC_MAP_PARTITIONS.
      mapPartitions: 1000,
    }
  },
  // add the middleware globally by adding
  router: {
    middleware: ["authentication"]
  },
  ui: {
    icons: ["mdi", "simple-icons"]
  },
  svgo: {
    // SVGs are imported explicitly (constants/sdgs.ts); there is no assets/icons/ folder to auto-register
    autoImportPath: false
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
});
