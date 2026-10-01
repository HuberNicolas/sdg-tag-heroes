// Number of API requests in flight, counted by plugins/api-activity.client.ts.
// Only used to show loading indicators; it does not change any request.
export default function useApiActivity() {
  const pending = useState<number>("api-pending", () => 0);
  const isBusy = computed(() => pending.value > 0);
  return { pending, isBusy };
}
