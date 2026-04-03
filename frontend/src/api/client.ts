import { apiBaseUrl } from "../config";

type ApiRequestOptions = {
  signal?: AbortSignal;
};

export async function apiRequest(path: string, options: ApiRequestOptions = {}): Promise<unknown> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      Accept: "application/json",
    },
    signal: options.signal,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${String(response.status)}.`);
  }

  return response.json();
}
