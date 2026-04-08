import { fireEvent, render, screen } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

describe("OverviewPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("shows a checking state while the health request is in flight", async () => {
    type FetchResponse = {
      ok: boolean;
      json: () => Promise<unknown>;
    };

    let resolveHealthFetch!: (value: FetchResponse) => void;

    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => {
        const requestUrl =
          typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;

        if (requestUrl.endsWith("/health")) {
          return new Promise((resolve) => {
            resolveHealthFetch = resolve;
          });
        }

        if (requestUrl.endsWith("/campaigns")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([]),
          });
        }

        throw new Error(`Unhandled request URL: ${requestUrl}`);
      }),
    );

    const { routes } = await import("../../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    render(<RouterProvider router={router} />);

    expect(screen.getByText("Checking")).toBeInTheDocument();

    resolveHealthFetch({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    });

    expect(await screen.findByText("Connected")).toBeInTheDocument();
  });

  it("shows the connected backend status inside the app shell", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ status: "ok" }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve([
              {
                id: "campaign-1",
                owner_id: "owner-1",
                name: "Shadows of Glass",
                description: "Urban intrigue campaign",
                created_at: "2026-04-08T12:00:00Z",
                updated_at: "2026-04-08T12:00:00Z",
              },
            ]),
        }),
    );

    const { routes } = await import("../../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "GM Workspace" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "GM Workspace" }).className).toContain(
      "font-cinzel",
    );
    expect(screen.getByRole("heading", { name: "Overview" }).className).toContain("font-ui");
    expect(screen.getByRole("link", { name: "World" })).toBeInTheDocument();
    expect(screen.queryByPlaceholderText("Quick find...")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Settings" })).not.toBeInTheDocument();
    expect(await screen.findByText("Connected")).toBeInTheDocument();
    expect(screen.getByText("Backend status: ok")).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Quick Draft" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Overview" })).toBeInTheDocument();
    expect(screen.queryByText("Global View")).toBeNull();
    expect(screen.queryByRole("button", { name: "New Entry" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "New Entity" })).toHaveAttribute(
      "href",
      "/entities/new",
    );
    const newCampaignLink = screen.getByRole("link", { name: "New Campaign" });
    expect(newCampaignLink).toHaveAttribute("href", "/campaigns/new");
    expect(newCampaignLink.className).toContain("secondary-button");
    expect(screen.getByRole("heading", { name: "Session Scratchpad" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Recent Entities" })).toBeInTheDocument();
    expect(screen.getByText("Type quick notes here... they save locally.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Shadows of Glass" })).toHaveAttribute(
      "href",
      "/campaigns/campaign-1",
    );
    expect(
      screen.queryByText("Open a campaign from the list to keep working."),
    ).not.toBeInTheDocument();
  });

  it("shows an error state when the health response payload is invalid", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ state: "ok" }),
      }),
    );

    const { routes } = await import("../../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByText("Offline")).toBeInTheDocument();
    expect(screen.getByText("Offline Mode: Backend Disconnected")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reconnect" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Quick Draft" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Recent Entities" })).toBeInTheDocument();
    expect(screen.getByText("Invalid health response payload.")).toBeInTheDocument();
    expect(
      screen.getByText("To enable AI extraction and sync, run the server:"),
    ).toBeInTheDocument();
  });

  it("aborts the health request on unmount without rendering an error state", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    const fetchSpy = vi.fn().mockImplementation(
      (_input: RequestInfo | URL, init?: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init?.signal?.addEventListener("abort", () => {
            reject(new DOMException("The operation was aborted.", "AbortError"));
          });
        }),
    );

    vi.stubGlobal("fetch", fetchSpy);

    const { routes } = await import("../../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    const { unmount } = render(<RouterProvider router={router} />);

    unmount();

    await Promise.resolve();

    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });

  it("keeps quick draft notes locally even when the backend is offline", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("connect ECONNREFUSED 127.0.0.1:8000")),
    );

    const { routes } = await import("../../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    render(<RouterProvider router={router} />);

    const quickDraft = await screen.findByRole("textbox", { name: "Quick Draft" });
    fireEvent.change(quickDraft, { target: { value: "King's brother hides in the east tower." } });

    expect(window.localStorage.getItem("gm-workspace:quick-draft")).toBe(
      "King's brother hides in the east tower.",
    );
    expect(screen.getByText("Offline")).toBeInTheDocument();
  });

  it("shows an honest empty state when there are no campaign shortcuts yet", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ status: "ok" }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([]),
        }),
    );

    const { routes } = await import("../../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    render(<RouterProvider router={router} />);

    expect(await screen.findByText("No campaigns yet.")).toBeInTheDocument();
    expect(
      screen.queryByText("Open a campaign from the list to keep working."),
    ).not.toBeInTheDocument();
  });

  it("renders the reference icon language in the shell and overview surfaces", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://example.test/api");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ status: "ok" }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([]),
        }),
    );

    const { routes } = await import("../../app/routes");
    const router = createMemoryRouter(routes, {
      initialEntries: ["/"],
    });

    const { container } = render(<RouterProvider router={router} />);

    expect(await screen.findByRole("heading", { name: "Overview" })).toBeInTheDocument();
    expect(container.querySelectorAll(".shell-header svg").length).toBeGreaterThanOrEqual(1);
    expect(container.querySelectorAll(".shell-nav svg").length).toBeGreaterThanOrEqual(5);
    expect(
      container.querySelectorAll(".overview-context-header svg").length,
    ).toBeGreaterThanOrEqual(1);
    expect(container.querySelectorAll(".overview-card svg").length).toBeGreaterThanOrEqual(2);
    expect(container.querySelector(".nav-link")).not.toBeNull();
    expect(getComputedStyle(container.querySelector(".nav-link") as Element).gap).not.toBe("0px");
  });
});
