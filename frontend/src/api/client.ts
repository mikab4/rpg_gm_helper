import { apiBaseUrl } from "../config";

export async function apiRequest<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${String(response.status)}.`);
  }

  return (await response.json()) as T;
}
