import { afterEach, describe, expect, it, vi } from "vitest";

describe("frontend compatibility API", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("loads the entity type compatibility report", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: () =>
        Promise.resolve({
          has_issues: true,
          issue_count: 1,
          issues: [
            {
              legacy_type: "npc",
              raw_variants: ["NPC", " npc "],
              count: 2,
              example_entities: [
                {
                  entity_id: "entity-1",
                  entity_name: "Rowan",
                  campaign_id: "campaign-1",
                  campaign_name: "Shadows of Glass",
                },
              ],
            },
          ],
        }),
    });

    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal("fetch", fetchSpy);

    const { getEntityTypeCompatibilityReport } = await import("../api/compatibility");

    await expect(getEntityTypeCompatibilityReport()).resolves.toMatchObject({
      hasIssues: true,
      issueCount: 1,
      issues: [{ legacyType: "npc", rawVariants: ["NPC", " npc "], count: 2 }],
    });

    const firstCall = fetchSpy.mock.calls[0] as [string, RequestInit] | undefined;
    expect(firstCall?.[0]).toBe("http://example.test/api/compatibility/entity-types");
  });

  it("submits explicit entity type migration mappings", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      json: () =>
        Promise.resolve({
          updated_count: 3,
          updated_types: [
            { legacy_type: "faction", target_type: "organization", updated_count: 1 },
            { legacy_type: "npc", target_type: "person", updated_count: 2 },
          ],
        }),
    });

    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal("fetch", fetchSpy);

    const { applyEntityTypeMigration } = await import("../api/compatibility");

    await expect(
      applyEntityTypeMigration([
        { legacyType: "npc", targetType: "person" },
        { legacyType: "faction", targetType: "organization" },
      ]),
    ).resolves.toMatchObject({
      updatedCount: 3,
      updatedTypes: [
        { legacyType: "faction", targetType: "organization", updatedCount: 1 },
        { legacyType: "npc", targetType: "person", updatedCount: 2 },
      ],
    });

    const firstCall = fetchSpy.mock.calls[0] as [string, RequestInit] | undefined;
    expect(firstCall?.[0]).toBe("http://example.test/api/compatibility/entity-types/migrate");
    expect(firstCall?.[1]).toMatchObject({
      body: JSON.stringify({
        mappings: [
          { legacy_type: "npc", target_type: "person" },
          { legacy_type: "faction", target_type: "organization" },
        ],
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST",
    });
  });
});
