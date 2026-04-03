import { apiBaseUrl } from "../config";

export async function apiRequest(path: string): Promise<unknown> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${String(response.status)}.`);
  }

  return response.json();
}
