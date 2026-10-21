import { defineNuxtPlugin } from "#app";

// Counts the API requests in flight for the loading indicators (useApiActivity).
// Wraps the global $fetch with hooks only; requests and responses stay unchanged.
export default defineNuxtPlugin({
  name: "api-activity",
  enforce: "pre",
  setup() {
    const { pending } = useApiActivity();
    const done = () => {
      pending.value = Math.max(0, pending.value - 1);
    };
    globalThis.$fetch = globalThis.$fetch.create({
      onRequest() {
        pending.value++;
      },
      onResponse: done,
      onRequestError: done,
    });
  },
});
