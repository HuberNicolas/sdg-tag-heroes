import * as d3 from "d3";

/*
 * HUD-style publication map, drawn with d3 (replaces Plotly).
 *
 * It takes the same trace objects the map code built for Plotly and fires the same events with the same
 * payloads (plotly_selected, plotly_click, plotly_hover, plotly_unhover, plotly_doubleclick), so the store
 * logic in scatterPlot.ts / scatterSDGPlot.ts stays as it was:
 *
 *   const map = createHexMap(container);
 *   map.on("plotly_selected", (e) => e.points.map((p) => p.pointNumber));
 *   map.react([scatterData, hoverMarker, userMarker]);
 *
 * Trace roles: the first trace without `role` holds the publications; `role: "hover"`, `"selected"` and
 * `"user"` are the highlight of a hovered row, the clicked publication and the point of interest.
 *
 * Marks keep their pixel size while zooming (semantic zoom), so zooming in separates overlapping cells.
 */

type Trace = {
  role?: "hover" | "selected" | "user";
  x: number[];
  y: number[];
  text?: string[] | string;
  marker?: {
    size?: number | number[];
    symbol?: string | string[];
    color?: string | string[];
    line?: { width?: number | number[]; color?: string | string[] };
  };
};

type PlotlyLikePoint = { pointNumber: number; x: number; y: number; data: Trace };
type Handler = (event?: { points: PlotlyLikePoint[] }) => void;

const pick = <T>(value: T | T[] | undefined, i: number, fallback: T): T =>
  Array.isArray(value) ? (value[i] ?? fallback) : (value ?? fallback);

// Flat-top hexagon and diamond around (0, 0)
const hexPath = (r: number) =>
  d3.range(6).map((k) => [r * Math.cos((Math.PI / 3) * k), r * Math.sin((Math.PI / 3) * k)].join(",")).join(" ");
const diamondPath = (r: number) => `0,${-r * 1.15} ${r * 1.15},0 0,${r * 1.15} ${-r * 1.15},0`;

const ICONS = {
  lasso:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M7 21c1.5-1 2-2.5 1.6-4"/><ellipse cx="13" cy="9.5" rx="8" ry="5.5" stroke-dasharray="3 2.5"/><circle cx="8.4" cy="15.3" r="1.6"/></svg>',
  pan: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M3 12h18M12 3l-3 3M12 3l3 3M12 21l-3-3M12 21l3-3M3 12l3-3M3 12l3 3M21 12l-3-3M21 12l-3 3"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  minus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12h14"/></svg>',
  reset:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 15v5h-5M4 4l6 6M20 20l-6-6"/></svg>',
};

export function createHexMap(container: HTMLElement) {
  const handlers: Record<string, Handler[]> = {};
  const emit = (name: string, event?: { points: PlotlyLikePoint[] }) =>
    (handlers[name] || []).forEach((h) => {
      try {
        h(event);
      } catch (error) {
        console.error(`[hexMap] ${name} handler failed`, error);
      }
    });

  let mode: "lasso" | "pan" = "lasso";
  let data: Trace | null = null;
  let overlays: Trace[] = [];
  let selection = new Set<number>();
  let transform = d3.zoomIdentity;
  let width = 0;
  let height = 0;
  let drawn = false;

  // ---------- DOM ----------
  const root = d3.select(container);
  root.selectAll("*").remove();
  root.classed("hexmap", true);

  const svg = root.append("svg").attr("class", "hexmap__svg");
  const gGrid = svg.append("g").attr("class", "hexmap__grid");
  const gMarks = svg.append("g").attr("class", "hexmap__marks");
  const gOverlay = svg.append("g").attr("class", "hexmap__overlay");
  const gCross = svg.append("g").attr("class", "hexmap__cross").style("display", "none");
  const crossX = gCross.append("line");
  const crossY = gCross.append("line");
  const lassoPath = svg.append("path").attr("class", "hexmap__lasso");

  ["tl", "tr", "bl", "br"].forEach((c) => root.append("span").attr("class", `hexmap__corner hexmap__corner--${c}`));

  const tooltip = root.append("div").attr("class", "hexmap__tooltip");
  const empty = root.append("div").attr("class", "hexmap__empty");
  empty.html(
    '<span class="hexmap__empty-icon">⬡</span><span>no publications on the map</span><small>select a topic above or try another universe</small>',
  );

  const toolbar = root.append("div").attr("class", "hexmap__toolbar");
  const modeGroup = toolbar.append("div").attr("class", "hexmap__seg");
  const btn = (parent: d3.Selection<HTMLDivElement, unknown, null, undefined>, icon: string, title: string, onClick: () => void) =>
    parent
      .append("button")
      .attr("type", "button")
      .attr("class", "hexmap__btn")
      .attr("title", title)
      .attr("aria-label", title)
      .html(icon)
      .on("click", (event: MouseEvent) => {
        event.stopPropagation();
        onClick();
      });
  const lassoBtn = btn(modeGroup, ICONS.lasso, "Lasso selection (drag)", () => setMode("lasso"));
  const panBtn = btn(modeGroup, ICONS.pan, "Pan (drag)", () => setMode("pan"));
  const zoomGroup = toolbar.append("div").attr("class", "hexmap__seg");
  btn(zoomGroup, ICONS.plus, "Zoom in", () => svg.transition().duration(250).call(zoom.scaleBy, 1.5));
  btn(zoomGroup, ICONS.minus, "Zoom out", () => svg.transition().duration(250).call(zoom.scaleBy, 1 / 1.5));
  btn(zoomGroup, ICONS.reset, "Reset view (double-click)", () => resetZoom());

  const status = root.append("div").attr("class", "hexmap__status");
  const statusCount = status.append("span");
  const statusZoom = status.append("span");
  const statusCursor = status.append("span").attr("class", "hexmap__cursor");
  root
    .append("div")
    .attr("class", "hexmap__hint")
    .text("drag: lasso · click: select · scroll: zoom · dbl-click: reset");

  // ---------- Scales ----------
  const baseX = d3.scaleLinear();
  const baseY = d3.scaleLinear();
  const zx = () => transform.rescaleX(baseX);
  const zy = () => transform.rescaleY(baseY);

  const fitDomain = () => {
    const xs = data?.x ?? [];
    const ys = data?.y ?? [];
    const pad = (ext: [number, number]) => {
      const span = ext[1] - ext[0] || 1;
      return [ext[0] - span * 0.08, ext[1] + span * 0.08] as [number, number];
    };
    baseX.domain(xs.length ? pad(d3.extent(xs) as [number, number]) : [0, 1]);
    baseY.domain(ys.length ? pad(d3.extent(ys) as [number, number]) : [0, 1]);
  };

  const measure = () => {
    const rect = container.getBoundingClientRect();
    width = Math.max(rect.width, 50);
    height = Math.max(rect.height, 50);
    svg.attr("width", width).attr("height", height).attr("viewBox", `0 0 ${width} ${height}`);
    baseX.range([16, width - 16]);
    baseY.range([height - 34, 44]);
    zoom.extent([[0, 0], [width, height]]);
  };

  // ---------- Zoom ----------
  const zoom = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 24])
    // Wheel zooms in both modes; dragging pans only in pan mode (in lasso mode it draws the lasso)
    .filter((event: Event) => {
      if (event.type === "dblclick") return false;
      if (event.type === "wheel") return true;
      return mode === "pan" && !(event as MouseEvent).button;
    })
    .on("zoom", (event) => {
      transform = event.transform;
      draw();
    });
  svg.call(zoom).on("dblclick.zoom", null);

  const resetZoom = () => svg.transition().duration(350).call(zoom.transform, d3.zoomIdentity);

  const setMode = (m: "lasso" | "pan") => {
    mode = m;
    lassoBtn.classed("is-active", m === "lasso");
    panBtn.classed("is-active", m === "pan");
    root.attr("data-mode", m);
  };
  setMode("lasso");

  // ---------- Drawing ----------
  const point = (i: number): PlotlyLikePoint => ({ pointNumber: i, x: data!.x[i], y: data!.y[i], data: data! });

  const drawGrid = () => {
    const x = zx();
    const y = zy();
    const xt = x.ticks(Math.max(2, Math.round(width / 110)));
    const yt = y.ticks(Math.max(2, Math.round(height / 90)));
    gGrid
      .selectAll<SVGLineElement, number>("line.v")
      .data(xt, (d) => d)
      .join("line")
      .attr("class", "v")
      .attr("x1", (d) => x(d))
      .attr("x2", (d) => x(d))
      .attr("y1", 0)
      .attr("y2", height);
    gGrid
      .selectAll<SVGLineElement, number>("line.h")
      .data(yt, (d) => d)
      .join("line")
      .attr("class", "h")
      .attr("y1", (d) => y(d))
      .attr("y2", (d) => y(d))
      .attr("x1", 0)
      .attr("x2", width);
    gGrid
      .selectAll<SVGTextElement, number>("text.vx")
      .data(xt, (d) => d)
      .join("text")
      .attr("class", "vx")
      .attr("x", (d) => x(d) + 4)
      .attr("y", height - 26)
      .text((d) => d3.format(".1f")(d));
    gGrid
      .selectAll<SVGTextElement, number>("text.hy")
      .data(yt, (d) => d)
      .join("text")
      .attr("class", "hy")
      .attr("x", 6)
      .attr("y", (d) => y(d) - 4)
      .text((d) => d3.format(".1f")(d));
  };

  const drawMarks = () => {
    if (!data) return;
    const x = zx();
    const y = zy();
    const hasSelection = selection.size > 0;
    const idx = d3.range(data.x.length);

    gMarks
      .selectAll<SVGPolygonElement, number>("polygon.mark")
      .data(idx, (i) => String(i))
      .join(
        (enter) =>
          enter
            .append("polygon")
            .attr("class", "mark")
            .on("pointerenter", (event: PointerEvent, i: number) => {
              showTooltip(event, i);
              emit("plotly_hover", { points: [point(i)] });
            })
            .on("pointermove", (event: PointerEvent, i: number) => showTooltip(event, i))
            .on("pointerleave", () => {
              tooltip.classed("is-visible", false);
              emit("plotly_unhover");
            })
            .on("pointerdown", (event: PointerEvent) => event.stopPropagation())
            .on("click", (event: MouseEvent, i: number) => {
              event.stopPropagation();
              emit("plotly_click", { points: [point(i)] });
            }),
        (update) => update,
        (exit) => exit.remove(),
      )
      .attr("points", (i) => {
        const r = pick(data!.marker?.size, i, 10) / 2 + 2;
        return pick(data!.marker?.symbol, i, "hexagon2") === "diamond" ? diamondPath(r) : hexPath(r);
      })
      .attr("transform", (i) => `translate(${x(data!.x[i])},${y(data!.y[i])})`)
      .attr("fill", (i) => pick(data!.marker?.color, i, "rgb(var(--c-fg-faint))") || "rgb(var(--c-fg-faint))")
      // An outline colour that differs from the fill encodes something (SDG map: fill = world SDG,
      // outline = top SDG of the publication); otherwise the outline is a thin gap in the background colour
      .attr("stroke", (i) => {
        const fill = pick(data!.marker?.color, i, "");
        const line = pick(data!.marker?.line?.color, i, "");
        return line && line !== fill && line !== "black" ? line : null;
      })
      .classed("is-ringed", (i) => {
        const fill = pick(data!.marker?.color, i, "");
        const line = pick(data!.marker?.line?.color, i, "");
        return !!line && line !== fill && line !== "black";
      })
      .classed("is-quest", (i) => pick(data!.marker?.symbol, i, "hexagon2") === "diamond")
      .classed("is-dim", (i) => hasSelection && !selection.has(i))
      .classed("is-selected", (i) => hasSelection && selection.has(i));
  };

  const drawOverlays = () => {
    const x = zx();
    const y = zy();
    const items = overlays.filter((t) => t && t.role && t.x?.length);
    const groups = gOverlay
      .selectAll<SVGGElement, Trace>("g.ov")
      .data(items, (t) => t.role!)
      .join((enter) => {
        const g = enter.append("g").attr("class", (t) => `ov ov--${t.role}`);
        g.each(function (t) {
          const s = d3.select(this);
          if (t.role === "hover") {
            s.append("polygon").attr("class", "ov__ring").attr("points", hexPath(17));
            s.append("polygon").attr("class", "ov__ring ov__ring--outer").attr("points", hexPath(25));
          } else if (t.role === "selected") {
            const b = 16;
            const l = 7;
            [
              [-b, -b, 1, 1],
              [b, -b, -1, 1],
              [-b, b, 1, -1],
              [b, b, -1, -1],
            ].forEach(([cx, cy, sx, sy]) =>
              s.append("path").attr("class", "ov__bracket").attr("d", `M${cx},${cy + sy * l}V${cy}H${cx + sx * l}`),
            );
            s.append("circle").attr("class", "ov__dot").attr("r", 2);
          } else if (t.role === "user") {
            s.append("circle").attr("class", "ov__pulse").attr("r", 10);
            s.append("path")
              .attr("class", "ov__pin")
              .attr("d", "M0,0 C-7,-9 -9,-13 -9,-17 A9,9 0 1 1 9,-17 C9,-13 7,-9 0,0 Z");
            s.append("circle").attr("class", "ov__pin-hole").attr("cx", 0).attr("cy", -17).attr("r", 3.2);
            s.append("text").attr("class", "ov__label").attr("x", 12).attr("y", -20).text("you");
          }
        });
        return g;
      });
    groups.attr("transform", (t) => `translate(${x(t.x[0])},${y(t.y[0])})`);
  };

  const draw = () => {
    if (!width) measure();
    drawGrid();
    drawMarks();
    drawOverlays();
    const n = data?.x.length ?? 0;
    statusCount.html(`n=<b>${n}</b>${selection.size ? ` · sel=<b>${selection.size}</b>` : ""}`);
    statusZoom.text(`zoom ${transform.k.toFixed(1)}×`);
    empty.classed("is-visible", drawn && n === 0);
  };

  // ---------- Tooltip ----------
  const showTooltip = (event: PointerEvent, i: number) => {
    if (!data) return;
    const raw = pick(data.text as string[] | string, i, "");
    const title = String(raw).split(/<br\s*\/?>/i)[0].replace(/^\s*Title:\s*/i, "").trim();
    const color = pick(data.marker?.color, i, "#888");
    const quest = pick(data.marker?.symbol, i, "hexagon2") === "diamond";
    tooltip
      .html(
        `<span class="hexmap__tt-swatch" style="background:${color}"></span>` +
          `<span class="hexmap__tt-body"><span class="hexmap__tt-title"></span>` +
          `<span class="hexmap__tt-meta">${quest ? "◆ quest publication · " : ""}x ${data.x[i].toFixed(2)} · y ${data.y[i].toFixed(2)}</span></span>`,
      )
      .classed("is-visible", true);
    tooltip.select(".hexmap__tt-title").text(title);
    const [mx, my] = d3.pointer(event, container);
    const tw = (tooltip.node() as HTMLElement).offsetWidth;
    tooltip.style("left", `${Math.min(mx + 14, width - tw - 8)}px`).style("top", `${my + 14}px`);
  };

  // ---------- Crosshair ----------
  svg.on("pointermove.cross", (event: PointerEvent) => {
    const [mx, my] = d3.pointer(event, svg.node());
    gCross.style("display", null);
    crossX.attr("x1", mx).attr("x2", mx).attr("y1", 0).attr("y2", height);
    crossY.attr("y1", my).attr("y2", my).attr("x1", 0).attr("x2", width);
    statusCursor.text(`x ${zx().invert(mx).toFixed(2)} · y ${zy().invert(my).toFixed(2)}`);
  });
  svg.on("pointerleave.cross", () => {
    gCross.style("display", "none");
    statusCursor.text("");
  });

  // ---------- Lasso ----------
  let lasso: [number, number][] | null = null;
  svg.on("pointerdown.lasso", (event: PointerEvent) => {
    if (mode !== "lasso" || event.button !== 0 || !data) return;
    lasso = [d3.pointer(event, svg.node())];
    (svg.node() as SVGSVGElement).setPointerCapture(event.pointerId);
  });
  svg.on("pointermove.lasso", (event: PointerEvent) => {
    if (!lasso) return;
    lasso.push(d3.pointer(event, svg.node()));
    lassoPath.attr("d", `M${lasso.join("L")}Z`).classed("is-visible", true);
  });
  svg.on("pointerup.lasso pointercancel.lasso", () => {
    if (!lasso || !data) return;
    const polygon = lasso;
    lasso = null;
    lassoPath.classed("is-visible", false);
    // A click (no real lasso) keeps the current selection
    const xs = polygon.map((p) => p[0]);
    const ys = polygon.map((p) => p[1]);
    if (polygon.length < 4 || (d3.max(xs)! - d3.min(xs)! < 6 && d3.max(ys)! - d3.min(ys)! < 6)) return;
    const x = zx();
    const y = zy();
    const inside = d3.range(data.x.length).filter((i) => d3.polygonContains(polygon, [x(data!.x[i]), y(data!.y[i])]));
    selection = new Set(inside);
    draw();
    emit("plotly_selected", { points: inside.map(point) });
  });

  svg.on("dblclick", () => {
    resetZoom();
    emit("plotly_doubleclick");
  });

  // ---------- Resize ----------
  const ro = new ResizeObserver(() => {
    measure();
    draw();
  });
  ro.observe(container);

  return {
    on(name: string, handler: Handler) {
      (handlers[name] ||= []).push(handler);
    },
    // Same role as Plotly.react: draw the given traces; extra arguments (Plotly layout) are ignored
    react(traces: (Trace | null | undefined)[], ..._ignored: unknown[]) {
      const list = traces.filter(Boolean) as Trace[];
      const next = list.find((t) => !t.role) ?? null;
      if (next !== data) {
        const firstData = !data || data.x.length === 0;
        if (next && data && next.x.length !== data.x.length) selection = new Set();
        data = next;
        if (firstData) fitDomain();
      }
      overlays = list.filter((t) => t.role);
      if (!drawn) {
        drawn = true;
        measure();
        fitDomain();
        container.dispatchEvent(new CustomEvent("hexmap:ready"));
      }
      draw();
    },
    resetZoom,
    destroy() {
      ro.disconnect();
      root.selectAll("*").remove();
    },
  };
}
