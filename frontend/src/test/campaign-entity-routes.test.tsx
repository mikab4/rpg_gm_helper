import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

type MockJsonResponse = {
  ok: boolean;
  status?: number;
  body?: unknown;
};

function jsonResponse(response: MockJsonResponse): Response {
  return {
    headers: new Headers({ "Content-Type": "application/json" }),
    json: () => Promise.resolve(response.body),
    ok: response.ok,
    status: response.status ?? 200,
  } as Response;
}

function getRequestUrl(input: RequestInfo | URL): string {
  if (typeof input === "string") {
    return input;
  }

  if (input instanceof URL) {
    return input.toString();
  }

  return input.url;
}

describe("campaign and entity frontend routes", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
    vi.resetModules();
    window.localStorage.clear();
  });

  it("renders the campaigns page with fetched campaigns", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({
          ok: true,
          body: [
            {
              id: "campaign-1",
              owner_id: "owner-1",
              name: "Shadows of Glass",
              description: "Urban intrigue campaign",
              created_at: "2026-04-08T12:00:00Z",
              updated_at: "2026-04-08T12:00:00Z",
            },
          ],
        }),
      ),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "Campaigns" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "New Campaign" })).toBeInTheDocument();
    expect(await screen.findByText("Shadows of Glass")).toBeInTheDocument();
    expect(screen.getByText("Urban intrigue campaign")).toBeInTheDocument();
    expect(screen.getByText(/Last Updated/i)).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Campaign List" })).toBeNull();
    expect(
      screen.getByRole("link", { name: "Open workspace for Shadows of Glass" }),
    ).toHaveAttribute("href", "/campaigns/campaign-1");
    expect(screen.queryByRole("link", { name: "Edit" })).toBeNull();
  });

  it("renders the campaign card itself as the workspace link", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({
          ok: true,
          body: [
            {
              id: "campaign-1",
              owner_id: "owner-1",
              name: "Shadows of Glass",
              description: "Urban intrigue campaign",
              created_at: "2026-04-08T12:00:00Z",
              updated_at: "2026-04-08T12:00:00Z",
            },
          ],
        }),
      ),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns"],
    });

    render(<RouterProvider router={router} />);

    const campaignLink = await screen.findByRole("link", {
      name: "Open workspace for Shadows of Glass",
    });

    expect(campaignLink).toHaveAttribute("href", "/campaigns/campaign-1");
    expect(screen.getByText("Shadows of Glass").closest("a")).toBe(campaignLink);
  });

  it("renders the campaign workspace overview by default", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({
          ok: true,
          body: {
            id: "campaign-1",
            owner_id: "owner-1",
            name: "Shadows of Glass",
            description: "Urban intrigue campaign",
            created_at: "2026-04-08T12:00:00Z",
            updated_at: "2026-04-08T12:00:00Z",
          },
        }),
      ),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1"],
    });

    const { container } = render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "Shadows of Glass" })).toHaveClass("font-ui");
    expect(screen.getByRole("link", { name: "Back to Registry" })).toHaveAttribute(
      "href",
      "/campaigns",
    );
    expect(
      within(screen.getByRole("navigation", { name: "Campaign Sections" })).getByRole("link", {
        name: "Overview",
      }),
    ).toHaveAttribute("aria-current", "page");
    expect(
      within(screen.getByRole("navigation", { name: "Campaign Sections" })).getByRole("link", {
        name: "Entities",
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Campaign Summary" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Recent Activity" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Quick Notes" })).toBeInTheDocument();
    expect(screen.getByText("Urban intrigue campaign")).toBeInTheDocument();
    expect(container.querySelector(".workspace-surface")).not.toBeNull();
    expect(
      screen.queryByText("Create a campaign workspace before adding campaign-specific entities."),
    ).toBeNull();
    expect(
      screen.queryByText(
        "Keep campaign descriptions short and practical in v1 so the table remains easy to scan.",
      ),
    ).toBeNull();
    expect(
      screen.queryByText(
        "This is the campaign cockpit summary: enough orientation to stay in flow now, with room for notes, relationships, and extraction surfaces later.",
      ),
    ).toBeNull();
  });

  it("keeps campaign quick notes locally across remounts", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({
          ok: true,
          body: {
            id: "campaign-1",
            owner_id: "owner-1",
            name: "Shadows of Glass",
            description: "Urban intrigue campaign",
            created_at: "2026-04-08T12:00:00Z",
            updated_at: "2026-04-08T12:00:00Z",
          },
        }),
      ),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1"],
    });

    const { unmount } = render(<RouterProvider router={router} />);

    const quickNotes = await screen.findByRole("textbox", { name: "Quick Notes" });
    fireEvent.change(quickNotes, {
      target: { value: "Remember the king's brother knows the east gate signal." },
    });

    expect(window.localStorage.getItem("gm-workspace:campaign-quick-notes:campaign-1")).toBe(
      "Remember the king's brother knows the east gate signal.",
    );

    unmount();

    const remountRouter = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1"],
    });

    render(<RouterProvider router={remountRouter} />);

    expect(await screen.findByRole("textbox", { name: "Quick Notes" })).toHaveValue(
      "Remember the king's brother knows the east gate signal.",
    );
  });

  it("exposes edit and delete actions from the campaign workspace", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    const fetchSpy = vi.fn().mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const requestUrl = getRequestUrl(input);

      if (requestUrl.endsWith("/campaigns/campaign-1") && init?.method !== "DELETE") {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            body: {
              id: "campaign-1",
              owner_id: "owner-1",
              name: "Shadows of Glass",
              description: "Urban intrigue campaign",
              created_at: "2026-04-08T12:00:00Z",
              updated_at: "2026-04-08T12:00:00Z",
            },
          }),
        );
      }

      if (requestUrl.endsWith("/campaigns/campaign-1") && init?.method === "DELETE") {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            status: 204,
          }),
        );
      }

      if (requestUrl.endsWith("/campaigns")) {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            body: [],
          }),
        );
      }

      throw new Error(`Unhandled request URL: ${requestUrl}`);
    });

    vi.stubGlobal("fetch", fetchSpy);

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByRole("link", { name: "Edit Campaign" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/edit",
    );

    fireEvent.click(screen.getByRole("button", { name: "Delete Campaign" }));

    expect(await screen.findByRole("heading", { name: "Campaign deleted" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to Campaigns" })).toHaveAttribute(
      "href",
      "/campaigns",
    );

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(
        "http://example.test/api/campaigns/campaign-1",
        expect.objectContaining({
          method: "DELETE",
        }),
      );
    });
  });

  it("renders campaign-scoped entities inside the campaign workspace", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const requestUrl = getRequestUrl(input);

        if (requestUrl.endsWith("/campaigns/campaign-1")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        if (requestUrl.endsWith("/campaigns/campaign-1/entities")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: [
                {
                  id: "entity-1",
                  campaign_id: "campaign-1",
                  type: "npc",
                  name: "Magistrate Ilya",
                  summary: "City official",
                  metadata: {},
                  source_document_id: null,
                  provenance_excerpt: null,
                  provenance_data: {},
                  created_at: "2026-04-08T12:00:00Z",
                  updated_at: "2026-04-08T12:00:00Z",
                },
              ],
            }),
          );
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1/entities"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "Shadows of Glass" })).toBeInTheDocument();
    expect(await screen.findByText("Magistrate Ilya")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Entity Roster" })).toBeNull();
    expect(screen.getByRole("link", { name: "New Entity" })).toBeInTheDocument();
    expect(screen.getByText("NPC")).toBeInTheDocument();
    expect(screen.getByText("City official")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Edit Magistrate Ilya" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/entities/entity-1/edit",
    );
    expect(screen.queryByRole("button", { name: "Quick look Magistrate Ilya" })).toBeNull();
    expect(screen.queryByRole("link", { name: "Open" })).toBeNull();
  });

  it("opens a quick-look side panel from the campaign workspace entity list", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const requestUrl = getRequestUrl(input);

        if (requestUrl.endsWith("/campaigns/campaign-1")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        if (requestUrl.endsWith("/campaigns/campaign-1/entities")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: [
                {
                  id: "entity-1",
                  campaign_id: "campaign-1",
                  type: "npc",
                  name: "Magistrate Ilya",
                  summary: "Brother of Rowan, magistrate of the lower ward.",
                  metadata: {},
                  source_document_id: null,
                  provenance_excerpt: null,
                  provenance_data: {},
                  created_at: "2026-04-08T12:00:00Z",
                  updated_at: "2026-04-08T12:00:00Z",
                },
              ],
            }),
          );
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1/entities"],
    });

    render(<RouterProvider router={router} />);

    fireEvent.click(await screen.findByText("Magistrate Ilya"));

    const quickLookPanel = await screen.findByRole("complementary", { name: "Entity quick look" });
    expect(quickLookPanel.className).toContain("quick-look-panel-paper");

    expect(within(quickLookPanel).getByRole("heading", { name: "Summary" })).toBeInTheDocument();
    expect(
      within(quickLookPanel).queryByText(
        "npc record in active use. Open the full record for campaign notes, editing, and deeper provenance.",
      ),
    ).toBeNull();
    expect(
      within(quickLookPanel).getByText("Brother of Rowan, magistrate of the lower ward."),
    ).toBeInTheDocument();
    expect(within(quickLookPanel).getByRole("link", { name: "Full Profile" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/entities/entity-1",
    );
    expect(within(quickLookPanel).getByRole("link", { name: "Edit Entity" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/entities/entity-1/edit",
    );
  });

  it("refetches the global entities page when the campaign filter changes", async () => {
    const fetchSpy = vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const requestUrl = getRequestUrl(input);

      if (requestUrl.endsWith("/campaigns")) {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            body: [
              {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            ],
          }),
        );
      }

      if (requestUrl.endsWith("/entities")) {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            body: [
              {
                id: "entity-1",
                campaign_id: "campaign-1",
                type: "npc",
                name: "Magistrate Ilya",
                summary: "City official",
                metadata: {},
                source_document_id: null,
                provenance_excerpt: null,
                provenance_data: {},
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            ],
          }),
        );
      }

      if (requestUrl.endsWith("/entities?campaign_id=campaign-1")) {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            body: [
              {
                id: "entity-2",
                campaign_id: "campaign-1",
                type: "location",
                name: "Broken Observatory",
                summary: "Hidden ruin",
                metadata: {},
                source_document_id: null,
                provenance_excerpt: null,
                provenance_data: {},
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            ],
          }),
        );
      }

      throw new Error(`Unhandled request URL: ${requestUrl}`);
    });

    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal("fetch", fetchSpy);

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/entities"],
    });

    const { container } = render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "World Browser" })).toBeInTheDocument();
    expect(container.querySelector(".workspace-surface")).not.toBeNull();
    expect(
      screen.getByText(
        "Browse the world-facing index across campaigns, then open any record in its campaign-owned detail view.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(
        "Use the campaign filter to narrow the list without losing the global entity entry point.",
      ),
    ).toBeNull();
    expect(
      screen.queryByText(
        "Entity rows keep their campaign context visible so global browsing does not hide ownership.",
      ),
    ).toBeNull();
    expect(await screen.findByText("Magistrate Ilya")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Edit Magistrate Ilya" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/entities/entity-1/edit",
    );

    fireEvent.change(screen.getByLabelText("Campaign"), {
      target: { value: "campaign-1" },
    });

    expect(await screen.findByText("Broken Observatory")).toBeInTheDocument();

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(
        "http://example.test/api/entities?campaign_id=campaign-1",
        expect.objectContaining({
          method: "GET",
        }),
      );
    });
  });

  it("opens quick look from a world entity row and routes edit back to the campaign-owned page", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const requestUrl = getRequestUrl(input);

        if (requestUrl.endsWith("/campaigns")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: [
                {
                  id: "campaign-1",
                  owner_id: "owner-1",
                  name: "Shadows of Glass",
                  description: "Urban intrigue campaign",
                  created_at: "2026-04-08T12:00:00Z",
                  updated_at: "2026-04-08T12:00:00Z",
                },
              ],
            }),
          );
        }

        if (requestUrl.endsWith("/entities")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: [
                {
                  id: "entity-1",
                  campaign_id: "campaign-1",
                  type: "npc",
                  name: "Magistrate Ilya",
                  summary: "Brother of Rowan, magistrate of the lower ward.",
                  metadata: {},
                  source_document_id: null,
                  provenance_excerpt: null,
                  provenance_data: {},
                  created_at: "2026-04-08T12:00:00Z",
                  updated_at: "2026-04-08T12:00:00Z",
                },
              ],
            }),
          );
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/entities"],
    });

    render(<RouterProvider router={router} />);

    fireEvent.click(await screen.findByText("Magistrate Ilya"));

    const quickLookPanel = await screen.findByRole("complementary", { name: "Entity quick look" });
    expect(quickLookPanel.className).toContain("quick-look-panel-paper");

    expect(within(quickLookPanel).getByRole("link", { name: "Full Profile" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/entities/entity-1",
    );
    expect(within(quickLookPanel).getByRole("link", { name: "Edit Entity" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/entities/entity-1/edit",
    );
  });

  it("renders the entity full profile on the main entity route", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const requestUrl = getRequestUrl(input);

        if (requestUrl.endsWith("/campaigns/campaign-1")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        if (requestUrl.endsWith("/campaigns/campaign-1/entities/entity-1")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "entity-1",
                campaign_id: "campaign-1",
                type: "npc",
                name: "Magistrate Ilya",
                summary: "Brother of Rowan, magistrate of the lower ward.",
                metadata: {},
                source_document_id: null,
                provenance_excerpt: null,
                provenance_data: {},
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1/entities/entity-1"],
    });

    const { container } = render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "Magistrate Ilya" })).toBeInTheDocument();
    expect(container.querySelector(".workspace-surface")).not.toBeNull();
    expect(screen.getByRole("heading", { name: "Summary" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Edit Entity" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1/entities/entity-1/edit",
    );
    expect(screen.queryByRole("button", { name: "Save Entity" })).toBeNull();
  });

  it("renders the entity editor on the edit route", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const requestUrl = getRequestUrl(input);

        if (requestUrl.endsWith("/campaigns/campaign-1")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        if (requestUrl.endsWith("/campaigns/campaign-1/entities/entity-1")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "entity-1",
                campaign_id: "campaign-1",
                type: "npc",
                name: "Magistrate Ilya",
                summary: "Brother of Rowan, magistrate of the lower ward.",
                metadata: {},
                source_document_id: null,
                provenance_excerpt: null,
                provenance_data: {},
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1/entities/entity-1/edit"],
    });

    const { container } = render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "Edit Entity" })).toBeInTheDocument();
    expect(container.querySelector(".workspace-surface")).not.toBeNull();
    expect(screen.getByRole("button", { name: "Save Entity" })).toBeInTheDocument();
    expect(screen.getByLabelText("Type")).toHaveDisplayValue("NPC");
    expect(screen.getByRole("option", { name: "Faction" })).toBeInTheDocument();
  });

  it("requires campaign selection on the global new entity page", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const requestUrl = getRequestUrl(input);

        if (requestUrl.endsWith("/campaigns")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: [
                {
                  id: "campaign-1",
                  owner_id: "owner-1",
                  name: "Shadows of Glass",
                  description: "Urban intrigue campaign",
                  created_at: "2026-04-08T12:00:00Z",
                  updated_at: "2026-04-08T12:00:00Z",
                },
              ],
            }),
          );
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/entities/new"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "New Entity" })).toBeInTheDocument();
    expect(
      screen.queryByText(
        "Create a new entity from the global entity tab while still choosing its owning campaign.",
      ),
    ).toBeNull();
    expect(
      screen.queryByText(
        "Metadata stays hidden in step 6 to keep the entity editor focused on the core CRUD path.",
      ),
    ).toBeNull();
    expect(screen.getByLabelText("Type")).toHaveValue("");

    fireEvent.click(screen.getByRole("button", { name: "Create Entity" }));

    expect(await screen.findByText("Campaign is required.")).toBeInTheDocument();
  });

  it("keeps the campaign-scoped new entity page free of plan-document wording", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal("fetch", vi.fn());

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1/entities/new"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "New Entity" })).toBeInTheDocument();
    expect(
      screen.queryByText("Create a new entity directly inside this campaign workspace."),
    ).toBeNull();
    expect(
      screen.queryByText(
        "Metadata stays hidden in step 6 to keep the entity editor focused on the core CRUD path.",
      ),
    ).toBeNull();
  });

  it("filters world entities by typed name before campaign or type narrowing", async () => {
    const fetchSpy = vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const requestUrl = getRequestUrl(input);

      if (requestUrl.endsWith("/campaigns")) {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            body: [
              {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            ],
          }),
        );
      }

      if (requestUrl.endsWith("/entities")) {
        return Promise.resolve(
          jsonResponse({
            ok: true,
            body: [
              {
                id: "entity-1",
                campaign_id: "campaign-1",
                type: "NPC",
                name: "Zam Grimbot",
                summary: "Timelord ruler of Wappana.",
                metadata: {},
                source_document_id: null,
                provenance_excerpt: null,
                provenance_data: {},
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
              {
                id: "entity-2",
                campaign_id: "campaign-1",
                type: "Location",
                name: "Broken Observatory",
                summary: "Hidden ruin",
                metadata: {},
                source_document_id: null,
                provenance_excerpt: null,
                provenance_data: {},
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            ],
          }),
        );
      }

      throw new Error(`Unhandled request URL: ${requestUrl}`);
    });

    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal("fetch", fetchSpy);

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/entities"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByText("Zam Grimbot")).toBeInTheDocument();
    expect(screen.getByText("Broken Observatory")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Search"), {
      target: { value: "zam" },
    });

    expect(await screen.findByText("Zam Grimbot")).toBeInTheDocument();
    expect(screen.queryByText("Broken Observatory")).toBeNull();

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(2);
    });
  });

  it("shows a user-facing error when entity delete fails from the edit page", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
        const requestUrl = getRequestUrl(input);

        if (requestUrl.endsWith("/campaigns/campaign-1")) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        if (
          requestUrl.endsWith("/campaigns/campaign-1/entities/entity-1") &&
          init?.method !== "DELETE"
        ) {
          return Promise.resolve(
            jsonResponse({
              ok: true,
              body: {
                id: "entity-1",
                campaign_id: "campaign-1",
                type: "npc",
                name: "Magistrate Ilya",
                summary: "Brother of Rowan, magistrate of the lower ward.",
                metadata: {},
                source_document_id: null,
                provenance_excerpt: null,
                provenance_data: {},
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            }),
          );
        }

        if (
          requestUrl.endsWith("/campaigns/campaign-1/entities/entity-1") &&
          init?.method === "DELETE"
        ) {
          return Promise.resolve(
            jsonResponse({
              ok: false,
              status: 404,
              body: {
                detail: "Entity no longer exists.",
              },
            }),
          );
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/campaigns/campaign-1/entities/entity-1/edit"],
    });

    render(<RouterProvider router={router} />);

    fireEvent.click(await screen.findByRole("button", { name: "Delete Entity" }));

    expect(await screen.findByText("Entity no longer exists.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Delete Entity" })).toBeEnabled();
  });
});
