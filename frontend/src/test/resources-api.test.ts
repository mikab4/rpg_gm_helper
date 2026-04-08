import { afterEach, describe, expect, it, vi } from "vitest";

describe("frontend resource APIs", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("loads the default owner", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            id: "0ea5d4df-868d-4643-b788-404c1c8bc85e",
            email: "gm@example.com",
            display_name: "Local GM",
            created_at: "2026-04-08T12:00:00Z",
            updated_at: "2026-04-08T12:00:00Z",
          }),
      }),
    );

    const { getDefaultOwner } = await import("../api/owners");

    await expect(getDefaultOwner()).resolves.toMatchObject({
      id: "0ea5d4df-868d-4643-b788-404c1c8bc85e",
      email: "gm@example.com",
      displayName: "Local GM",
    });
  });

  it("lists campaigns from the campaign collection endpoint", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    });

    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal("fetch", fetchSpy);

    const { listCampaigns } = await import("../api/campaigns");

    await listCampaigns();

    const firstCall = fetchSpy.mock.calls[0] as [string, RequestInit] | undefined;

    expect(firstCall).toBeDefined();
    expect(firstCall?.[0]).toBe("http://example.test/api/campaigns");
    expect(firstCall?.[1]).toMatchObject({
      headers: {
        Accept: "application/json",
      },
      method: "GET",
    });
  });

  it("creates entities through the campaign-scoped endpoint", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          id: "5dc2d3f5-0f84-48c2-b728-7c89fb30d04b",
          campaign_id: "c53594e5-c721-46dc-8f88-70273d8de676",
          type: "npc",
          name: "Ilya",
          summary: "Magistrate",
          metadata: {},
          source_document_id: null,
          provenance_excerpt: null,
          provenance_data: {},
          created_at: "2026-04-08T12:00:00Z",
          updated_at: "2026-04-08T12:00:00Z",
        }),
    });

    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal("fetch", fetchSpy);

    const { createEntity } = await import("../api/entities");

    await createEntity("c53594e5-c721-46dc-8f88-70273d8de676", {
      type: "npc",
      name: "Ilya",
      summary: "Magistrate",
      metadata: {},
    });

    const firstCall = fetchSpy.mock.calls[0] as [string, RequestInit] | undefined;

    expect(firstCall).toBeDefined();
    expect(firstCall?.[0]).toBe(
      "http://example.test/api/campaigns/c53594e5-c721-46dc-8f88-70273d8de676/entities",
    );
    expect(firstCall?.[1]).toMatchObject({
      body: JSON.stringify({
        type: "npc",
        name: "Ilya",
        summary: "Magistrate",
        metadata: {},
      }),
      headers: {
        "Content-Type": "application/json",
      },
      method: "POST",
    });
  });

  it("surfaces backend error details as readable messages", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        headers: new Headers({ "Content-Type": "application/json" }),
        json: () => Promise.resolve({ detail: "Campaign not found." }),
      }),
    );

    const { getCampaign } = await import("../api/campaigns");

    await expect(getCampaign("missing-campaign")).rejects.toThrow("Campaign not found.");
  });
});
