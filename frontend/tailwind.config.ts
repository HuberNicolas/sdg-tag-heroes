import type { Config } from "tailwindcss";

import daisyui from "daisyui";

export default {
  content: [],
  theme: {
    extend: {
      colors: {
        customGray: {
          50:  '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563', // This will be used as primary in light mode (defaults to 500/400 depending on theme)
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
        customStone: {
          50:  '#FAFAFA',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A8A29E', // This is your desired secondary shade
          500: '#78716C',
          600: '#57534E',
          700: '#44403C',
          800: '#292524',
          900: '#1C1917',
        },
      }
    }
  },
  plugins: [
    daisyui
  ],
  daisyui: {
    themes: ["light", "black"],
  },
} satisfies Config;
