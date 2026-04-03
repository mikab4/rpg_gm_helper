const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

if (!configuredApiBaseUrl) {
  throw new Error("VITE_API_BASE_URL is required.");
}

export const apiBaseUrl: string = configuredApiBaseUrl;
