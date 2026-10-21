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
  app: {
    head: {
      title: "SDG Tag Heroes",
      htmlAttrs: { lang: "en" },
      meta: [
        { name: "description", content: "A game to label research publications with the UN Sustainable Development Goals." }
      ],
      link: [{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }]
    }
  },
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
  // Light and dark theme: the class `light` / `dark` on <html> drives Tailwind, Nuxt UI and the tokens in
  // assets/css/tailwind.css; data-theme drives daisyUI. The first visit follows the operating system.
  colorMode: {
    preference: "system",
    fallback: "light",
    classSuffix: "",
    dataValue: "theme",
    storageKey: "sdg-tag-heroes-color-mode"
  },
  fonts: {
    families: [
      { name: "Space Grotesk", provider: "google", weights: [400, 500, 600, 700] },
      { name: "JetBrains Mono", provider: "google", weights: [400, 500, 600, 700] },
      // Pixel font for the logo and the universe names
      { name: "Press Start 2P", provider: "google" }
    ]
  },
  watch: ['composables/**/*.ts', 'components/**/*.vue'], // does not trigger new build
});
