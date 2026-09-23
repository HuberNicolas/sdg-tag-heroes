import type { Ref } from "vue";
import { useDebounceFn, useResizeObserver } from "@vueuse/core";

/**
 * Calls `redraw` (debounced) whenever the element changes its size, e.g. when the
 * window is resized or a panel next to it grows. The first measurement is ignored,
 * because charts draw themselves on mount.
 *
 * Only the width is tracked by default: most charts set their own height, and
 * reacting to it would redraw in a loop.
 */
export function useRedrawOnResize(
  target: Ref<HTMLElement | null | undefined>,
  redraw: () => void,
  { trackHeight = false, delay = 150 } = {},
) {
  let lastWidth = -1;
  let lastHeight = -1;
  const debouncedRedraw = useDebounceFn(redraw, delay);

  useResizeObserver(target, (entries) => {
    const { width, height } = entries[0].contentRect;
    const changed =
      Math.abs(width - lastWidth) >= 1 || (trackHeight && Math.abs(height - lastHeight) >= 1);
    const isFirstMeasurement = lastWidth < 0;

    lastWidth = width;
    lastHeight = height;

    if (changed && !isFirstMeasurement && width > 0) {
      debouncedRedraw();
    }
  });
}
