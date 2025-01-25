/*
To address the issue of mapping between snake_case (used in your Python backend)
and camelCase (used in your TypeScript frontend), you can implement a
transformation layer that converts the keys from one format to the other.
This can be done either on the backend or the frontend,
but it's often more convenient to handle it
on the frontend to keep the backend
code clean and consistent with its conventions.
 */

export function snakeToCamel(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(snakeToCamel);
  } else if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      acc[camelKey] = snakeToCamel(obj[key]);
      return acc;
    }, {} as any);
  }
  return obj;
}
