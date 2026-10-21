import type { Config } from "tailwindcss";

import daisyui from "daisyui";

// Semantic colours read the CSS variables in assets/css/tailwind.css, so one class works in light and dark mode
const token = (name: string) => `rgb(var(--c-${name}) / <alpha-value>)`;

export default {
  content: [],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Space Grotesk", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
        pixel: ['"Press Start 2P"', "JetBrains Mono", "monospace"],
      },
      colors: {
        bg: token("bg"),
        surface: token("surface"),
        "surface-2": token("surface-2"),
        muted: token("muted"),
        "muted-strong": token("muted-strong"),
        fg: token("fg"),
        "fg-dim": token("fg-dim"),
        "fg-faint": token("fg-faint"),
        // Lines carry their own alpha
        line: "rgb(var(--c-line))",
        "line-strong": "rgb(var(--c-line-strong))",
        accent: token("accent"),
        "hero-blue": token("blue"),
        "hero-violet": token("violet"),
        "hero-amber": token("amber"),
        "hero-red": token("red"),
        "hero-pink": token("pink"),
        tooltip: token("tooltip"),

        // Primary colour of Nuxt UI (buttons, toggles, focus rings): the portfolio green.
        // Nuxt UI uses 500 in light mode and 400 in dark mode.
        hero: {
          50: "#effef7",
          100: "#dcfcee",
          200: "#bdf9de",
          300: "#8ff5c9",
          400: "#5cf0b0",
          500: "#0a8f60",
          600: "#087a52",
          700: "#0a6345",
          800: "#0b4f38",
          900: "#0a3f2e",
          950: "#04241a",
        },
        // Neutral of Nuxt UI: a cool ink that matches the dark background (#08080c)
        ink: {
          50: "#f6f6f9",
          100: "#ececf2",
          200: "#dcdce6",
          300: "#c2c2d1",
          400: "#9a9aad",
          500: "#6e6e85",
          600: "#52526a",
          700: "#3a3a4d",
          800: "#1c1c2a",
          900: "#12121d",
          950: "#08080c",
        },
      },
      // A bare `border` uses the theme line colour instead of a fixed gray
      borderColor: {
        DEFAULT: "rgb(var(--c-line))",
      },
      borderRadius: {
        panel: "14px",
      },
      boxShadow: {
        panel: "var(--shadow)",
        glow: "0 8px 30px rgb(var(--c-accent) / 0.18)",
      },
      keyframes: {
        "fade-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "none" },
        },
        "hex-spin": {
          "0%": { transform: "rotate(0deg) scale(1)" },
          "50%": { transform: "rotate(180deg) scale(0.85)" },
          "100%": { transform: "rotate(360deg) scale(1)" },
        },
        blink: {
          "50%": { opacity: "0" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.6s cubic-bezier(0.22, 1, 0.36, 1) both",
        "hex-spin": "hex-spin 2.4s cubic-bezier(0.65, 0, 0.35, 1) infinite",
        blink: "blink 1.1s step-end infinite",
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    // A few components (drawer, cards, steps, modal) come from daisyUI. Its themes follow the colour mode, which
    // sets data-theme="light" / "dark" on <html> (see colorMode.dataValue in nuxt.config.ts).
    themes: [
      {
        light: {
          primary: "#0a8f60",
          "primary-content": "#ffffff",
          secondary: "#2a6ad0",
          accent: "#0a8f60", // same as the `accent` token: daisyUI also defines bg-accent
          neutral: "#15151f",
          "neutral-content": "#f6f6f9",
          "base-100": "#ffffff",
          "base-200": "#f6f6f9",
          "base-300": "#ececf2",
          "base-content": "#15151f",
          "--rounded-box": "14px",
          "--rounded-btn": "10px",
        },
      },
      {
        dark: {
          primary: "#5cf0b0",
          "primary-content": "#08080c",
          secondary: "#6eb5ff",
          accent: "#5cf0b0",
          neutral: "#1c1c2a",
          "neutral-content": "#eaeaf2",
          "base-100": "#0e0e15",
          "base-200": "#12121c",
          "base-300": "#1a1a26",
          "base-content": "#eaeaf2",
          "--rounded-box": "14px",
          "--rounded-btn": "10px",
        },
      },
    ],
    darkTheme: "dark",
    logs: false,
  },
} satisfies Config;
