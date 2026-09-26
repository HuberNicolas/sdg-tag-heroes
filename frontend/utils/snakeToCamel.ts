/*
To address the issue of mapping between snake_case (used in your Python backend)
and camelCase (used in your TypeScript frontend), you can implement a
transformation layer that converts the keys from one format to the other.
This can be done either on the backend or the frontend,
but it's often more convenient to handle it
on the frontend to keep the backend
code clean and consistent with its conventions.
 */

// The result type is given by the caller, e.g. snakeToCamel<SDGGoalSchemaFull[]>(response)
export function snakeToCamel<T = unknown>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((item) => snakeToCamel(item)) as T;
  } else if (obj !== null && typeof obj === 'object') {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      result[camelKey] = snakeToCamel(value);
    }
    return result as T;
  }
  return obj as T;
}
