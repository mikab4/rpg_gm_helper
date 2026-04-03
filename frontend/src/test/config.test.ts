import { afterEach, describe, expect, it, vi } from "vitest";

describe("frontend config", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("reads VITE_API_BASE_URL from the environment", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");

    const { apiBaseUrl } = await import("../config");

    expect(apiBaseUrl).toBe("http://example.test/api");
  });

  it("throws when VITE_API_BASE_URL is missing", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "");

    await expect(import("../config")).rejects.toThrow("VITE_API_BASE_URL is required.");
  });
});
