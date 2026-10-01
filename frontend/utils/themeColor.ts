// Plotly cannot read CSS variables, so charts ask for the current theme colour as an rgb() string.
// `name` is a token from assets/css/tailwind.css without the prefix, e.g. "fg", "accent", "surface".
export function themeColor(name: string, alpha = 1): string {
  if (typeof window === "undefined") return `rgba(128, 128, 128, ${alpha})`;
  const raw = getComputedStyle(document.documentElement).getPropertyValue(`--c-${name}`).trim();
  // Tokens are "r g b" or "r g b / a"
  const [rgb, ownAlpha] = raw.split("/").map((part) => part.trim());
  const [r, g, b] = rgb.split(/\s+/).map(Number);
  const a = ownAlpha ? Number(ownAlpha) * alpha : alpha;
  return `rgba(${r}, ${g}, ${b}, ${a})`;
}

// Shared look of the publication maps (Plotly): hover labels, lasso, mode bar
export function mapTheme() {
  return {
    hoverlabel: {
      bgcolor: themeColor("surface", 0.96),
      bordercolor: themeColor("line-strong"),
      font: { family: "Space Grotesk, sans-serif", size: 12, color: themeColor("fg") },
      align: "left",
    },
    newselection: {
      line: { color: themeColor("accent"), width: 1.5, dash: "dot" },
    },
    activeselection: { fillcolor: themeColor("accent"), opacity: 0.08 },
    font: { family: "JetBrains Mono, monospace", color: themeColor("fg-dim") },
  };
}

export const mapConfig = {
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: ["toImage", "autoScale2d", "select2d"],
};
