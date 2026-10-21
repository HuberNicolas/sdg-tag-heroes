// Filter of the publication table by top SDG, set by clicking a bar in the selection summary (BarPlot.vue).
// null: no filter.
export default function useTopSdgFilter() {
  const topSdgFilter = useState<number | null>("top-sdg-filter", () => null);
  const toggleTopSdgFilter = (sdgId: number) => {
    topSdgFilter.value = topSdgFilter.value === sdgId ? null : sdgId;
  };
  const clearTopSdgFilter = () => {
    topSdgFilter.value = null;
  };
  return { topSdgFilter, toggleTopSdgFilter, clearTopSdgFilter };
}
