export default defineAppConfig({
  ui: {
    // Palettes from tailwind.config.ts: the portfolio green and a cool ink neutral
    primary: 'hero',
    gray: 'ink',
    button: {
      rounded: "rounded-full",
      font: "font-mono font-medium",
    },
    card: {
      background: "bg-surface/80 backdrop-blur-sm",
      ring: "ring-1 ring-line",
      divide: "divide-y divide-line",
      rounded: "rounded-panel",
      shadow: "shadow-panel",
    },
    modal: {
      overlay: {
        background: "bg-ink-950/50 dark:bg-ink-950/70 backdrop-blur-sm",
      },
      background: "bg-surface",
      ring: "ring-1 ring-line",
      rounded: "rounded-panel",
    },
    input: {
      rounded: "rounded-lg",
    },
    select: {
      rounded: "rounded-lg",
    },
    selectMenu: {
      rounded: "rounded-lg",
    },
    notifications: {
      // Show toasts at the top right of the screen
      position: 'top-0 bottom-[unset]'
    }
  },
});
